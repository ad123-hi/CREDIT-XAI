import sys
import pickle
import pandas as pd
import numpy as np
from utils.config import MODEL_PATH, PREPROCESSOR_PATH

class SafeLabelEncoder:
    """
    Must match the class structure used during training.
    Used by pickle for deserialization.
    """
    def __init__(self):
        self.mapping = {}
        self.default_val = 0
        self.classes_ = []

    def fit(self, series):
        unique_vals = sorted(series.dropna().astype(str).unique())
        self.classes_ = unique_vals
        self.mapping = {val: idx for idx, val in enumerate(unique_vals)}
        self.default_val = len(self.mapping)
        return self

    def transform(self, series):
        series_str = series.astype(str)
        return series_str.map(self.mapping).fillna(self.default_val).astype(int)

# Inject SafeLabelEncoder into all main modules to support multi-processing/uvicorn reload on Windows
for name, module in list(sys.modules.items()):
    if 'main' in name:
        try:
            setattr(module, 'SafeLabelEncoder', SafeLabelEncoder)
        except Exception:
            pass

def load_artifacts():
    """
    Load serialized model and preprocessor dictionary.
    """
    # Double-insure SafeLabelEncoder injection in active main modules
    for name, module in list(sys.modules.items()):
        if 'main' in name:
            try:
                setattr(module, 'SafeLabelEncoder', SafeLabelEncoder)
            except Exception:
                pass

    print(f"[*] Loading model from {MODEL_PATH}...")
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
        
    print(f"[*] Loading preprocessor from {PREPROCESSOR_PATH}...")
    with open(PREPROCESSOR_PATH, "rb") as f:
        preprocessor = pickle.load(f)
        
    return model, preprocessor

def preprocess_request(request_data: dict, preprocessor: dict) -> pd.DataFrame:
    """
    Apply identical preprocessing to the raw dictionary input as performed in training.
    1. Apply log transformation to annual_inc.
    2. Convert categorical columns to numeric using saved SafeLabelEncoder instances.
    3. Fill nulls using train-set means.
    4. Select and order columns matching training features.
    """
    # 1. Create a copy of the input
    data = request_data.copy()
    
    # 2. Feature Engineering: log_annual_inc
    data['log_annual_inc'] = np.log10(1 + data['annual_inc'])
    
    # 3. Build DataFrame
    df = pd.DataFrame([data])
    
    # 4. Encoding: Categoricals encoded via saved encoders
    encoders = preprocessor['encoders']
    categorical_cols = preprocessor['categorical_cols']
    for col in categorical_cols:
        if col in df.columns:
            le = encoders[col]
            df[col] = le.transform(df[col])
            
    # 5. Imputation: Fill missing values using saved training means
    imputer_means = preprocessor['imputer_means']
    df = df.fillna(imputer_means)
    
    # 6. Feature Selection & Ordering: Match training feature list exactly
    feature_cols = preprocessor['feature_cols']
    df_final = df[feature_cols]
    
    return df_final
