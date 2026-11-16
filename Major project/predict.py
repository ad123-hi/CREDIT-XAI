import os
import argparse
import pickle
import pandas as pd
import numpy as np

# Import SafeLabelEncoder so pickle can deserialize it
from train import SafeLabelEncoder

def load_inference_artifacts(model_path, preprocessor_path):
    print(f"[*] Loading model from {model_path}...")
    with open(model_path, "rb") as f:
        model = pickle.load(f)
        
    print(f"[*] Loading preprocessor from {preprocessor_path}...")
    with open(preprocessor_path, "rb") as f:
        preprocessor = pickle.load(f)
        
    return model, preprocessor

def preprocess_new_data(df, preprocessor):
    """
    Apply the exact preprocessing steps to new/unseen data using the saved artifacts.
    """
    print("[*] Preprocessing new data...")
    df_proc = df.copy()
    
    # 1. Handle term (split string and convert to int)
    if 'term' in df_proc.columns:
        from train import parse_term
        df_proc['term'] = df_proc['term'].apply(parse_term)
        
    # 2. Handle earliest_cr_line (extract year)
    if 'earliest_cr_line' in df_proc.columns:
        from train import parse_earliest_cr_line
        df_proc['earliest_cr_line'] = df_proc['earliest_cr_line'].apply(parse_earliest_cr_line)
        
    # 3. Handle annual_inc -> log_annual_inc
    if 'annual_inc' in df_proc.columns:
        df_proc['log_annual_inc'] = df_proc['annual_inc'].apply(lambda x: np.log10(1 + x) if pd.notna(x) else np.nan)
        df_proc.drop(labels=['annual_inc'], axis=1, inplace=True)
        
    # 4. Handle FICO ranges -> fico_score
    if 'fico_range_low' in df_proc.columns and 'fico_range_high' in df_proc.columns:
        df_proc['fico_score'] = 0.5 * df_proc['fico_range_low'] + 0.5 * df_proc['fico_range_high']
        df_proc.drop(labels=['fico_range_low', 'fico_range_high'], axis=1, inplace=True)
        
    # 5. Drop emp_length if present
    if 'emp_length' in df_proc.columns:
        df_proc.drop(labels=['emp_length'], axis=1, inplace=True)
        
    # 6. Apply Categorical Encoders fit on training data
    encoders = preprocessor['encoders']
    categorical_cols = preprocessor['categorical_cols']
    for col in categorical_cols:
        if col in df_proc.columns:
            le = encoders[col]
            df_proc[col] = le.transform(df_proc[col])
            
    # 7. Impute missing values using training means
    imputer_means = preprocessor['imputer_means']
    df_proc = df_proc.fillna(imputer_means)
    
    # 8. Reorder columns to match features expected by the model
    feature_cols = preprocessor['feature_cols']
    
    # Ensure all expected columns are present, fill with NaN if missing
    for col in feature_cols:
        if col not in df_proc.columns:
            print(f"[!] Warning: Expected feature '{col}' is missing from raw input. Filling with training mean.")
            df_proc[col] = imputer_means.get(col, 0.0)
            
    # Return features in the exact training order
    return df_proc[feature_cols]

def main():
    parser = argparse.ArgumentParser(description="Production Inference Script")
    parser.add_argument("--data_path", type=str, default="accepted_2007_to_2018Q4.csv.gz",
                        help="Path to raw CSV file containing records to predict")
    parser.add_argument("--num_records", type=int, default=5,
                        help="Number of records to predict on")
    parser.add_argument("--model_path", type=str, default="model.pkl",
                        help="Path to saved model.pkl")
    parser.add_argument("--preprocessor_path", type=str, default="preprocessor.pkl",
                        help="Path to saved preprocessor.pkl")
    args = parser.parse_args()
    
    # Load model and preprocessor
    if not os.path.exists(args.model_path) or not os.path.exists(args.preprocessor_path):
        print(f"[!] Error: Model or Preprocessor file not found. Please run train.py first.")
        return
        
    model, preprocessor = load_inference_artifacts(args.model_path, args.preprocessor_path)
    
    # Load sample records
    print(f"[*] Loading first {args.num_records} records from {args.data_path} for testing...")
    
    # Use cols list from preprocessor to only load required columns
    feature_cols = preprocessor['feature_cols']
    
    # Map back engineered features to original columns they represent
    original_cols_needed = []
    for col in feature_cols:
        if col == 'log_annual_inc':
            original_cols_needed.append('annual_inc')
        elif col == 'fico_score':
            original_cols_needed.extend(['fico_range_low', 'fico_range_high'])
        else:
            original_cols_needed.append(col)
            
    # Include loan_status if we want to print target comparison
    cols_to_load = list(set(original_cols_needed + ['loan_status']))
    
    df_raw = pd.read_csv(args.data_path, nrows=args.num_records, usecols=cols_to_load, compression='gzip')
    
    # Keep loan_status for comparison print
    loan_statuses = df_raw.get('loan_status', None)
    
    # Preprocess
    df_features = preprocess_new_data(df_raw, preprocessor)
    
    # Predict probabilities and classes
    probabilities = model.predict_proba(df_features)[:, 1]
    predictions = model.predict(df_features)
    
    print("\n" + "="*50)
    print("               INFERENCE RESULTS")
    print("="*50)
    for idx in range(len(df_raw)):
        status_str = f"Actual Loan Status: {loan_statuses.iloc[idx]}" if loan_statuses is not None else ""
        pred_label = "Charged Off" if predictions[idx] == 1 else "Fully Paid"
        print(f"Record {idx + 1}:")
        print(f"  {status_str}")
        print(f"  Predicted Probability of Default: {probabilities[idx]:.4f}")
        print(f"  Model Decision: {pred_label}")
        print("-"*30)
    print("="*50 + "\n")

if __name__ == "__main__":
    main()
