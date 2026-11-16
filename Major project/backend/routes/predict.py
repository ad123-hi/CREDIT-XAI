import time
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
import numpy as np
import pandas as pd
import shap

from utils.config import FEATURES_METADATA, MODEL_METRICS
from utils.schemas import (
    PredictionRequest, 
    PredictionResponse, 
    ExplainResponse, 
    ModelInfoResponse, 
    ShapContribution
)
from utils.preprocess import preprocess_request

router = APIRouter()

# Global variables initialized in app.py startup event
model = None
preprocessor = None
shap_explainer = None

def get_model():
    if model is None:
        raise HTTPException(status_code=503, detail="Model is not initialized.")
    return model

def get_preprocessor():
    if preprocessor is None:
        raise HTTPException(status_code=503, detail="Preprocessor is not initialized.")
    return preprocessor

def get_explainer():
    global shap_explainer
    if shap_explainer is None:
        if model is not None:
            print("[*] Initializing SHAP TreeExplainer...")
            shap_explainer = shap.TreeExplainer(model)
        else:
            raise HTTPException(status_code=503, detail="SHAP Explainer is not initialized.")
    return shap_explainer

@router.get("/features")
def get_features_metadata():
    """
    Returns metadata for every input feature.
    Used by the frontend to dynamically construct validation forms.
    """
    return FEATURES_METADATA

@router.get("/model-info", response_model=ModelInfoResponse)
def get_model_info(preprocessor=Depends(get_preprocessor)):
    """
    Returns model metrics and baseline details.
    """
    feature_names = preprocessor['feature_cols']
    return ModelInfoResponse(
        model_name=MODEL_METRICS["model_name"],
        algorithm=MODEL_METRICS["algorithm"],
        training_accuracy=MODEL_METRICS["training_accuracy"],
        precision=MODEL_METRICS["precision"],
        recall=MODEL_METRICS["recall"],
        f1_score=MODEL_METRICS["f1_score"],
        roc_auc=MODEL_METRICS["roc_auc"],
        version=MODEL_METRICS["version"],
        num_features=MODEL_METRICS["num_features"],
        feature_names=feature_names,
        confusion_matrix=MODEL_METRICS["confusion_matrix"]
    )

def determine_risk_category(prob: float) -> str:
    if prob < 0.20:
        return "Low Risk"
    elif prob < 0.45:
        return "Moderate Risk"
    elif prob < 0.70:
        return "High Risk"
    else:
        return "Very High Risk"

@router.post("/predict", response_model=PredictionResponse)
def predict_default(
    request: PredictionRequest,
    model=Depends(get_model),
    preprocessor=Depends(get_preprocessor)
):
    """
    Fast prediction endpoint that returns probability, confidence score, and risk category.
    """
    start_time = time.time()
    
    # Preprocess request dictionary
    request_dict = request.model_dump()
    df_features = preprocess_request(request_dict, preprocessor)
    
    # Predict default probability
    # GradientBoostingClassifier predict_proba returns [prob_0, prob_1]
    probabilities = model.predict_proba(df_features)[0]
    prob_default = float(probabilities[1])
    
    # Predict class (1 = Charged Off, 0 = Fully Paid)
    pred_code = int(model.predict(df_features)[0])
    prediction = "Charged Off" if pred_code == 1 else "Fully Paid"
    
    # Confidence is the probability of the predicted class
    confidence = prob_default if pred_code == 1 else (1.0 - prob_default)
    
    risk_cat = determine_risk_category(prob_default)
    duration_ms = (time.time() - start_time) * 1000.0
    
    return PredictionResponse(
        prediction=prediction,
        prediction_code=pred_code,
        default_probability=round(prob_default, 4),
        confidence=round(confidence, 4),
        risk_category=risk_cat,
        processing_time_ms=round(duration_ms, 2)
    )

@router.post("/explain", response_model=ExplainResponse)
def explain_default(
    request: PredictionRequest,
    model=Depends(get_model),
    preprocessor=Depends(get_preprocessor),
    explainer=Depends(get_explainer)
):
    """
    Prediction & Local Explainability endpoint.
    Computes predictions, SHAP values, feature attributions, and a plain English explanation.
    """
    start_time = time.time()
    
    # Preprocess request dictionary
    request_dict = request.model_dump()
    df_features = preprocess_request(request_dict, preprocessor)
    
    # Model predictions
    probabilities = model.predict_proba(df_features)[0]
    prob_default = float(probabilities[1])
    pred_code = int(model.predict(df_features)[0])
    prediction = "Charged Off" if pred_code == 1 else "Fully Paid"
    confidence = prob_default if pred_code == 1 else (1.0 - prob_default)
    risk_cat = determine_risk_category(prob_default)
    
    # Compute SHAP Values
    shap_vals = explainer.shap_values(df_features)[0]
    
    # Formulate attributions
    attributions = []
    feature_cols = preprocessor['feature_cols']
    
    for i, col in enumerate(feature_cols):
        raw_val = float(df_features.iloc[0, i])
        shap_val = float(shap_vals[i])
        
        # Determine human-friendly name
        meta = FEATURES_METADATA.get(col)
        if meta:
            label = meta["name"]
        else:
            # Map back engineered names to friendly names if needed
            if col == "log_annual_inc":
                label = "annual_inc"
            elif col == "fico_score":
                label = "fico_score"
            else:
                label = col
                
        effect = "increase_risk" if shap_val > 0 else "decrease_risk"
        
        attributions.append(ShapContribution(
            feature=col,
            feature_label=label,
            value=round(raw_val, 4),
            shap_value=round(shap_val, 6),
            importance=round(abs(shap_val), 6),
            effect=effect
        ))
        
    # Sort attributions by importance
    attributions.sort(key=lambda x: x.importance, reverse=True)
    
    # Generate Natural Language Explanation
    positives = [a for a in attributions if a.effect == "increase_risk"]
    negatives = [a for a in attributions if a.effect == "decrease_risk"]
    
    def get_friendly_desc(attr):
        # Format the value nicely
        val = attr.value
        name = attr.feature_label
        
        if name == "annual_inc" or name == "log_annual_inc":
            # Map log back to dollar amount
            dollar_val = request_dict.get("annual_inc", 10**val - 1)
            return f"annual income of ${int(dollar_val):,}"
        elif name == "loan_amnt" or name == "funded_amnt" or name == "last_pymnt_amnt" or name == "installment":
            return f"{name.replace('_', ' ')} of ${int(val):,}"
        elif name == "int_rate" or name == "dti" or name == "revol_util" or name == "bc_util":
            return f"{name.replace('_', ' ')} of {val:.1f}%"
        elif name == "fico_score":
            return f"FICO credit score of {int(val)}"
        elif name == "sub_grade" or name == "grade":
            # get original grade from request
            orig_grade = request_dict.get(name, val)
            return f"credit risk subgrade of {orig_grade}"
        elif name == "term":
            orig_term = request_dict.get("term", int(val))
            return f"loan term of {orig_term} months"
        else:
            orig_val = request_dict.get(name, val)
            return f"{name.replace('_', ' ')} of {orig_val}"
            
    # Compile text description
    explanation_parts = []
    if pred_code == 1:
        # High Risk explanation
        explanation_parts.append(
            f"The applicant is classified as {risk_cat} primarily due to "
        )
        if len(positives) >= 1:
            explanation_parts.append(f"a high risk {get_friendly_desc(positives[0])}")
        if len(positives) >= 2:
            explanation_parts.append(f", combined with an unfavorable {get_friendly_desc(positives[1])}")
        if len(positives) >= 3:
            explanation_parts.append(f" and an elevated {get_friendly_desc(positives[2])}")
            
        if len(negatives) >= 1:
            explanation_parts.append(
                f". Positive risk mitigators include a strong {get_friendly_desc(negatives[0])}"
            )
            if len(negatives) >= 2:
                explanation_parts.append(f" and a supportive {get_friendly_desc(negatives[1])}")
            explanation_parts.append(
                f", but these factors are not sufficient to outweigh the negative risk elements."
            )
    else:
        # Low Risk explanation
        explanation_parts.append(
            f"The applicant is classified as {risk_cat} because of a favorable "
        )
        if len(negatives) >= 1:
            explanation_parts.append(f"{get_friendly_desc(negatives[0])}")
        if len(negatives) >= 2:
            explanation_parts.append(f", a healthy {get_friendly_desc(negatives[1])}")
        if len(negatives) >= 3:
            explanation_parts.append(f" and a strong {get_friendly_desc(negatives[2])}")
            
        if len(positives) >= 1:
            explanation_parts.append(
                f". An unfavorable {get_friendly_desc(positives[0])}"
            )
            if len(positives) >= 2:
                explanation_parts.append(f" and an elevated {get_friendly_desc(positives[1])}")
            explanation_parts.append(
                f" increase the risk slightly, but they are well within acceptable thresholds."
            )
            
    explanation = "".join(explanation_parts)
    
    duration_ms = (time.time() - start_time) * 1000.0
    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return ExplainResponse(
        prediction=prediction,
        prediction_code=pred_code,
        default_probability=round(prob_default, 4),
        confidence=round(confidence, 4),
        risk_category=risk_cat,
        processing_time_ms=round(duration_ms, 2),
        shap_attributions=attributions,
        explanation=explanation,
        timestamp=timestamp_str
    )
