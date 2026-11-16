import os
import argparse
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split, KFold, cross_val_score, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import AdaBoostClassifier, GradientBoostingClassifier, RandomForestClassifier, ExtraTreesClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

class SafeLabelEncoder:
    """
    A robust wrapper for LabelEncoder that handles missing values and unseen categories
    gracefully, ensuring production safety for validation and inference.
    """
    def __init__(self):
        self.mapping = {}
        self.default_val = 0
        self.classes_ = []

    def fit(self, series):
        # Get unique sorted values from non-null string representations
        unique_vals = sorted(series.dropna().astype(str).unique())
        self.classes_ = unique_vals
        self.mapping = {val: idx for idx, val in enumerate(unique_vals)}
        self.default_val = len(self.mapping)
        return self

    def transform(self, series):
        series_str = series.astype(str)
        return series_str.map(self.mapping).fillna(self.default_val).astype(int)

def load_data(filepath, columns=None):
    """
    Load data from the compressed CSV file.
    """
    print(f"[*] Loading dataset from {filepath}...")
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Dataset not found at {filepath}")
    
    # Load only specified columns for a massive performance and memory boost
    if columns is not None:
        print(f"[*] Performance boost: loading only {len(columns)} necessary columns.")
        df = pd.read_csv(filepath, usecols=columns, compression='gzip', low_memory=False)
    else:
        df = pd.read_csv(filepath, compression='gzip', low_memory=False)
        
    print(f"[+] Loaded shape: {df.shape}")
    return df

def clean_and_filter(df):
    """
    Step 1: Label Check & Filtering
    Filter records where loan_status is 'Fully Paid' or 'Charged Off' and binarize the label.
    """
    print("[*] Filtering dataset for completed loans ('Fully Paid', 'Charged Off')...")
    df_filtered = df.loc[df['loan_status'].isin(['Fully Paid', 'Charged Off'])].copy()
    
    print("[*] Binarizing label variable 'charged_off'...")
    df_filtered['charged_off'] = (df_filtered['loan_status'] == 'Charged Off').apply(np.uint8)
    df_filtered.drop('loan_status', axis=1, inplace=True)
    
    print(f"[+] Filtered shape: {df_filtered.shape}")
    return df_filtered

def perform_feature_selection(df, run_correlation_check=True):
    """
    Steps 2-4: Feature Selection
    Includes:
    - Dropping features with >30% missing values.
    - Keeping only columns in the keep list.
    - Dropping numerical features with low correlation with the target (<0.03).
    - Dropping high cardinality categorical columns.
    """
    print("[*] Performing feature selection...")
    df_selected = df.copy()
    
    # 1. Drop features with >30% missing values
    missing_fractions = df_selected.isnull().mean().round(3)
    drop_list_missing = sorted(list(missing_fractions[missing_fractions > 0.3].index))
    if drop_list_missing:
        print(f"[*] Dropping {len(drop_list_missing)} columns with >30% missing values: {drop_list_missing}")
        df_selected.drop(labels=drop_list_missing, axis=1, inplace=True)
    
    # 2. Keep only columns based on intuitiveness keep list
    keep_list = [
        'charged_off', 'funded_amnt', 'addr_state', 'annual_inc', 'application_type', 
        'dti', 'earliest_cr_line', 'emp_length', 'emp_title', 'fico_range_high', 
        'fico_range_low', 'grade', 'home_ownership', 'id', 'initial_list_status', 
        'installment', 'int_rate', 'loan_amnt', 'mort_acc', 'open_acc', 
        'pub_rec', 'pub_rec_bankruptcies', 'purpose', 'revol_bal', 'revol_util', 
        'sub_grade', 'term', 'title', 'total_acc', 'verification_status', 
        'zip_code', 'last_pymnt_amnt', 'num_actv_rev_tl', 'mo_sin_rcnt_rev_tl_op', 
        'mo_sin_old_rev_tl_op', 'bc_util', 'bc_open_to_buy', 'avg_cur_bal', 'acc_open_past_24mths'
    ]
    keep_list_existing = [col for col in keep_list if col in df_selected.columns]
    drop_list_intuitiveness = [col for col in df_selected.columns if col not in keep_list_existing]
    if drop_list_intuitiveness:
        print(f"[*] Dropping {len(drop_list_intuitiveness)} columns not in keep list.")
        df_selected.drop(labels=drop_list_intuitiveness, axis=1, inplace=True)
        
    # 3. Correlation filter (< 0.03 correlation with target)
    if run_correlation_check:
        print("[*] Computing Pearson correlation matrix to filter low-correlation numeric features...")
        correlations = df_selected.corr(numeric_only=True)
        corr_charged_off = abs(correlations['charged_off']).sort_values(ascending=False)
        drop_list_corr = sorted(list(corr_charged_off[corr_charged_off < 0.03].index))
        if drop_list_corr:
            print(f"[*] Dropping {len(drop_list_corr)} low-correlation numeric columns (< 0.03): {drop_list_corr}")
            df_selected.drop(labels=drop_list_corr, axis=1, inplace=True)
            
    # 4. Drop high cardinality columns
    high_card_cols = ['id', 'emp_title', 'title', 'zip_code']
    high_card_existing = [col for col in high_card_cols if col in df_selected.columns]
    if high_card_existing:
        print(f"[*] Dropping high cardinality categorical columns: {high_card_existing}")
        df_selected.drop(labels=high_card_existing, axis=1, inplace=True)
        
    print(f"[+] Selected feature shape: {df_selected.shape}")
    return df_selected

def parse_term(val):
    if pd.isna(val):
        return np.nan
    s = str(val).strip()
    parts = s.split()
    if parts:
        try:
            return np.int8(parts[0])
        except ValueError:
            return np.nan
    return np.nan

def parse_emp_length(val):
    if pd.isna(val):
        return np.nan
    s = str(val).strip()
    if s == '10+ years':
        s = '10 years'
    elif s == '< 1 year':
        s = '0 years'
    parts = s.split()
    if parts:
        try:
            return np.int8(parts[0])
        except ValueError:
            return np.nan
    return np.nan

def parse_earliest_cr_line(val):
    if pd.isna(val):
        return np.nan
    s = str(val).strip()
    if len(s) >= 4:
        try:
            return int(s[-4:])
        except ValueError:
            return np.nan
    return np.nan

def engineer_features(df):
    """
    Step 5: Feature Engineering
    Transform term, earliest_cr_line, log_annual_inc, and fico_score.
    """
    print("[*] Engineering features...")
    df_engineered = df.copy()
    
    # 1. term
    if 'term' in df_engineered.columns:
        df_engineered['term'] = df_engineered['term'].apply(parse_term)
        
    # 2. emp_length -> process then drop as per notebook
    if 'emp_length' in df_engineered.columns:
        df_engineered['emp_length'] = df_engineered['emp_length'].apply(parse_emp_length)
        print("[*] Dropping 'emp_length' feature (minimal class variance observed)...")
        df_engineered.drop(labels=['emp_length'], axis=1, inplace=True)
        
    # 3. earliest_cr_line
    if 'earliest_cr_line' in df_engineered.columns:
        df_engineered['earliest_cr_line'] = df_engineered['earliest_cr_line'].apply(parse_earliest_cr_line)
        
    # 4. log_annual_inc
    if 'annual_inc' in df_engineered.columns:
        df_engineered['log_annual_inc'] = df_engineered['annual_inc'].apply(lambda x: np.log10(1 + x) if pd.notna(x) else np.nan)
        df_engineered.drop(labels=['annual_inc'], axis=1, inplace=True)
        
    # 5. fico_score
    if 'fico_range_low' in df_engineered.columns and 'fico_range_high' in df_engineered.columns:
        df_engineered['fico_score'] = 0.5 * df_engineered['fico_range_low'] + 0.5 * df_engineered['fico_range_high']
        df_engineered.drop(labels=['fico_range_low', 'fico_range_high'], axis=1, inplace=True)
        
    print(f"[+] Feature engineering completed. Shape: {df_engineered.shape}")
    return df_engineered

def split_and_sample(df, sample_size=10000, sample_seed=42, split_seed=7, test_size=0.2):
    """
    Step 6: Class Balancing and Train/Test Split
    """
    print(f"[*] Class balancing: Sampling {sample_size} records per class (Charged Off vs Fully Paid)...")
    if sample_size > 0:
        loanstatus_0 = df[df["charged_off"] == 0]
        loanstatus_1 = df[df["charged_off"] == 1]
        
        n_0 = min(len(loanstatus_0), sample_size)
        n_1 = min(len(loanstatus_1), sample_size)
        
        subset_loanstatus_0 = loanstatus_0.sample(n=n_0, random_state=sample_seed)
        subset_loanstatus_1 = loanstatus_1.sample(n=n_1, random_state=sample_seed)
        
        df_sampled = pd.concat([subset_loanstatus_1, subset_loanstatus_0])
        df_sampled = df_sampled.sample(frac=1, random_state=sample_seed).reset_index(drop=True)
    else:
        df_sampled = df.sample(frac=1, random_state=sample_seed).reset_index(drop=True)
        
    print(f"[+] Balanced dataset class distribution:")
    print(df_sampled['charged_off'].value_counts())
    
    Y = df_sampled['charged_off']
    X = df_sampled.drop(columns=['charged_off'])
    
    print(f"[*] Performing {int((1-test_size)*100)}/{int(test_size*100)} train/test split...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, Y, test_size=test_size, random_state=split_seed
    )
    
    print(f"[+] Train shape: X={X_train.shape}, y={y_train.shape}")
    print(f"[+] Test shape:  X={X_test.shape}, y={y_test.shape}")
    return X_train, X_test, y_train, y_test

def fit_preprocessing(X_train, categorical_cols):
    """
    Fit label encoders and calculate column-wise means only on the training split to avoid data leakage.
    """
    print("[*] Fitting preprocessing transformers on the training set to prevent data leakage...")
    encoders = {}
    X_train_encoded = X_train.copy()
    
    # 1. Fit and transform categorical columns
    for col in categorical_cols:
        if col in X_train.columns:
            le = SafeLabelEncoder()
            le.fit(X_train[col])
            encoders[col] = le
            X_train_encoded[col] = le.transform(X_train[col])
            
    # 2. Compute means of all columns (including newly encoded ones) for imputation
    imputer_means = X_train_encoded.mean(numeric_only=True)
    
    preprocessing_artifacts = {
        'encoders': encoders,
        'imputer_means': imputer_means,
        'categorical_cols': categorical_cols,
        'feature_cols': list(X_train.columns)
    }
    print("[+] Preprocessing fitting complete.")
    return preprocessing_artifacts

def transform_data(X, preprocessing_artifacts):
    """
    Transform raw features using the fitted label encoders and training imputer means.
    """
    X_trans = X.copy()
    encoders = preprocessing_artifacts['encoders']
    imputer_means = preprocessing_artifacts['imputer_means']
    categorical_cols = preprocessing_artifacts['categorical_cols']
    
    # Categorical label encoding
    for col in categorical_cols:
        if col in X_trans.columns:
            le = encoders[col]
            X_trans[col] = le.transform(X_trans[col])
            
    # Impute missing values using training means
    X_trans = X_trans.fillna(imputer_means)
    return X_trans

def run_model_comparison(X_train, y_train, seed=7, num_folds=10):
    """
    Evaluate 9 classification models using 10-fold cross validation.
    """
    print("\n" + "="*50)
    print("           MODEL COMPARISON & SPOT CHECKING")
    print("="*50)
    models = [
        ('LR', LogisticRegression(max_iter=1000)),
        ('LDA', LinearDiscriminantAnalysis()),
        ('KNN', KNeighborsClassifier()),
        ('CART', DecisionTreeClassifier()),
        ('NN', MLPClassifier(max_iter=500)),
        ('AB', AdaBoostClassifier()),
        ('GBM', GradientBoostingClassifier()),
        ('RF', RandomForestClassifier()),
        ('ET', ExtraTreesClassifier())
    ]
    
    results = []
    names = []
    scoring = 'roc_auc'
    
    for name, model in models:
        print(f"[*] Evaluating {name}...")
        kfold = KFold(n_splits=num_folds, shuffle=True, random_state=seed)
        cv_results = cross_val_score(model, X_train, y_train, cv=kfold, scoring=scoring)
        results.append(cv_results)
        names.append(name)
        print(f"  -> {name}: Mean ROC-AUC = {cv_results.mean():.6f} (std = {cv_results.std():.6f})")
    print("="*50 + "\n")

def tune_hyperparameters(X_train, y_train, seed=7, num_folds=10):
    """
    Perform grid search tuning for Gradient Boosting Classifier.
    """
    print("\n[*] Starting GridSearchCV for Gradient Boosting Classifier...")
    n_estimators = [20, 180, 250]
    max_depth = [2, 3, 5]
    param_grid = dict(n_estimators=n_estimators, max_depth=max_depth)
    
    model = GradientBoostingClassifier()
    kfold = KFold(n_splits=num_folds, shuffle=True, random_state=seed)
    
    grid = GridSearchCV(estimator=model, param_grid=param_grid, scoring='roc_auc', cv=kfold)
    grid_result = grid.fit(X_train, y_train)
    
    print(f"[+] Best: {grid_result.best_score_:.6f} using {grid_result.best_params_}")
    means = grid_result.cv_results_['mean_test_score']
    stds = grid_result.cv_results_['std_test_score']
    params = grid_result.cv_results_['params']
    ranks = grid_result.cv_results_['rank_test_score']
    
    for mean, std, param, rank in zip(means, stds, params, ranks):
        print(f"  #{rank} Mean: {mean:.6f} ({std:.6f}) with {param}")
        
    return grid_result.best_params_

def evaluate_model(model, X_test, y_test):
    """
    Evaluate the final model on the test dataset and generate accuracy,
    confusion matrix, and classification report.
    """
    print("\n" + "="*50)
    print("               FINAL MODEL EVALUATION")
    print("="*50)
    predictions = model.predict(X_test)
    acc = accuracy_score(y_test, predictions)
    print(f"ACCURACY SCORE on TEST set: {acc:.6f}")
    
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, predictions))
    
    print("\nClassification Report:")
    print(classification_report(y_test, predictions))
    
    # Feature Importance
    print("\nFeature Importances:")
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]
    
    features = list(X_test.columns)
    for f in range(X_test.shape[1]):
        print(f"  {f+1}. Feature '{features[indices[f]]}' : Importance = {importances[indices[f]]:.6f}")
    
    # Save Feature Importance Plot
    plt.figure(figsize=(10, 6))
    plt.title("Feature Importances")
    feat_importances = pd.Series(importances, index=features)
    feat_importances.nlargest(10).plot(kind='barh')
    plt.tight_layout()
    plt.savefig("feature_importances.png")
    print("[*] Saved feature importance plot as 'feature_importances.png'")
    print("="*50 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Production Training Pipeline for Lending Club Loan Default Prediction")
    parser.add_argument("--data_path", type=str, default="accepted_2007_to_2018Q4.csv.gz",
                        help="Path to the Lending Club CSV file (gzipped)")
    parser.add_argument("--sample_size", type=str, default="10000",
                        help="Number of records to sample per class (use 0 for all records)")
    parser.add_argument("--output_dir", type=str, default=".",
                        help="Directory to save final model and preprocessor artifacts")
    parser.add_argument("--run_comparison", action="store_true",
                        help="If set, executes cross-validation spot-checking on 9 classification algorithms")
    parser.add_argument("--run_tuning", action="store_true",
                        help="If set, executes GridSearchCV parameter search instead of using default best parameters")
    parser.add_argument("--seed", type=int, default=7,
                        help="Random seed for model splitting and cross-validation")
    parser.add_argument("--sample_seed", type=int, default=42,
                        help="Random seed for balanced class sampling")
    args = parser.parse_args()

    # Parse sample size
    try:
        sample_size = int(args.sample_size)
    except ValueError:
        sample_size = 10000

    # Ensure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)

    # 1. Performance Boost Check: Load only necessary columns
    keep_list = [
        'funded_amnt', 'addr_state', 'annual_inc', 'application_type', 'dti', 
        'earliest_cr_line', 'emp_length', 'emp_title', 'fico_range_high', 
        'fico_range_low', 'grade', 'home_ownership', 'id', 'initial_list_status', 
        'installment', 'int_rate', 'loan_amnt', 'mort_acc', 'open_acc', 
        'pub_rec', 'pub_rec_bankruptcies', 'purpose', 'revol_bal', 'revol_util', 
        'sub_grade', 'term', 'title', 'total_acc', 'verification_status', 
        'zip_code', 'last_pymnt_amnt', 'num_actv_rev_tl', 'mo_sin_rcnt_rev_tl_op', 
        'mo_sin_old_rev_tl_op', 'bc_util', 'bc_open_to_buy', 'avg_cur_bal', 
        'acc_open_past_24mths', 'loan_status'
    ]

    # Load data
    df = load_data(args.data_path, columns=keep_list)

    # Clean and filter target labels
    df_clean = clean_and_filter(df)

    # Perform Feature Selection
    df_selected = perform_feature_selection(df_clean, run_correlation_check=True)

    # Feature Engineering
    df_engineered = engineer_features(df_selected)

    # Train/Test split and balanced sampling
    X_train, X_test, y_train, y_test = split_and_sample(
        df_engineered, 
        sample_size=sample_size, 
        sample_seed=args.sample_seed, 
        split_seed=args.seed
    )

    # Detect Categorical Columns
    categorical_feature_mask = X_train.dtypes == object
    categorical_cols = X_train.columns[categorical_feature_mask].tolist()
    print(f"[*] Detected categorical columns: {categorical_cols}")

    # Fit preprocessing steps on the training data only
    preprocessor = fit_preprocessing(X_train, categorical_cols)

    # Transform Train and Test splits
    X_train_trans = transform_data(X_train, preprocessor)
    X_test_trans = transform_data(X_test, preprocessor)

    # Model comparison spot check (if requested)
    if args.run_comparison:
        run_model_comparison(X_train_trans, y_train, seed=args.seed)

    # Hyperparameter tuning
    if args.run_tuning:
        best_params = tune_hyperparameters(X_train_trans, y_train, seed=args.seed)
        params_max_depth = best_params['max_depth']
        params_n_estimators = best_params['n_estimators']
    else:
        # Defaults matching the notebook's grid search best parameters
        print("[*] Using default best parameters from notebook: max_depth=3, n_estimators=250")
        params_max_depth = 3
        params_n_estimators = 250

    # Fit Final Model
    print(f"[*] Fitting final Gradient Boosting Classifier (max_depth={params_max_depth}, n_estimators={params_n_estimators})...")
    final_model = GradientBoostingClassifier(max_depth=params_max_depth, n_estimators=params_n_estimators, random_state=args.seed)
    final_model.fit(X_train_trans, y_train)

    # Evaluate Model
    evaluate_model(final_model, X_test_trans, y_test)

    # Save final artifacts
    model_path = os.path.join(args.output_dir, "model.pkl")
    preprocessor_path = os.path.join(args.output_dir, "preprocessor.pkl")
    
    print(f"[*] Saving model artifact to {model_path}...")
    with open(model_path, "wb") as f:
        pickle.dump(final_model, f)
        
    print(f"[*] Saving preprocessing artifact to {preprocessor_path}...")
    with open(preprocessor_path, "wb") as f:
        pickle.dump(preprocessor, f)

    print("[+] Training pipeline finished successfully!")

if __name__ == "__main__":
    main()
