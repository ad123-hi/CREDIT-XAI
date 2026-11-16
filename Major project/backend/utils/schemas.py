from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class PredictionRequest(BaseModel):
    # Applicant Information
    annual_inc: float = Field(..., ge=0.0, le=10000000.0, description="Annual income of the borrower.", json_schema_extra={"example": 65000.0})
    emp_length: str = Field("10+ years", description="Employment length (e.g., '10+ years', '< 1 year'). Ignored by model but kept for metadata compliance.", json_schema_extra={"example": "10+ years"})
    home_ownership: str = Field(..., description="Home ownership status.", json_schema_extra={"example": "MORTGAGE"})
    verification_status: str = Field(..., description="Income verification status.", json_schema_extra={"example": "Not Verified"})
    purpose: str = Field(..., description="Purpose of the loan request.", json_schema_extra={"example": "debt_consolidation"})
    addr_state: str = Field(..., min_length=2, max_length=2, description="Two-letter US state code.", json_schema_extra={"example": "CA"})
    application_type: str = Field(..., description="Individual or Joint App.", json_schema_extra={"example": "Individual"})

    # Loan Information
    loan_amnt: float = Field(..., ge=500.0, le=40000.0, description="Requested loan amount.", json_schema_extra={"example": 10000.0})
    funded_amnt: float = Field(..., ge=500.0, le=40000.0, description="Funded loan amount.", json_schema_extra={"example": 10000.0})
    int_rate: float = Field(..., ge=5.31, le=30.99, description="Annual interest rate (%).", json_schema_extra={"example": 12.0})
    installment: float = Field(..., ge=4.93, le=1719.83, description="Monthly installment payment.", json_schema_extra={"example": 330.0})
    term: int = Field(..., description="Number of payment installments (36 or 60).", json_schema_extra={"example": 36})
    grade: str = Field(..., description="Lending Club loan grade.", json_schema_extra={"example": "B"})
    sub_grade: str = Field(..., description="Lending Club loan subgrade.", json_schema_extra={"example": "B1"})

    # Credit Profile
    fico_score: float = Field(..., ge=300.0, le=850.0, description="Borrower FICO Score.", json_schema_extra={"example": 700.0})
    dti: float = Field(..., ge=0.0, le=999.0, description="Debt-to-income ratio (%).", json_schema_extra={"example": 15.0})
    revol_util: float = Field(..., ge=0.0, le=150.0, description="Revolving utilization rate (%).", json_schema_extra={"example": 40.0})
    last_pymnt_amnt: float = Field(..., ge=0.0, le=40000.0, description="Last total payment amount received.", json_schema_extra={"example": 3000.0})
    acc_open_past_24mths: int = Field(..., ge=0, le=50, description="Accounts opened in past 24 months.", json_schema_extra={"example": 3})
    avg_cur_bal: float = Field(..., ge=0.0, le=1000000.0, description="Average current balance.", json_schema_extra={"example": 50000.0})
    bc_open_to_buy: float = Field(..., ge=0.0, le=500000.0, description="Bankcard open to buy credit line.", json_schema_extra={"example": 10000.0})
    bc_util: float = Field(..., ge=0.0, le=150.0, description="Bankcard utilization rate (%).", json_schema_extra={"example": 50.0})
    mo_sin_old_rev_tl_op: int = Field(..., ge=0, le=1000, description="Months since oldest revolving line opened.", json_schema_extra={"example": 120})
    mo_sin_rcnt_rev_tl_op: int = Field(..., ge=0, le=500, description="Months since most recent revolving line opened.", json_schema_extra={"example": 12})
    mort_acc: int = Field(..., ge=0, le=30, description="Number of mortgage accounts.", json_schema_extra={"example": 2})
    num_actv_rev_tl: int = Field(..., ge=0, le=40, description="Number of active revolving accounts.", json_schema_extra={"example": 4})
    initial_list_status: str = Field(..., description="Initial list status of the loan (w, f).", json_schema_extra={"example": "w"})
    earliest_cr_line: int = Field(..., ge=1940, le=2018, description="Year earliest credit line was opened.", json_schema_extra={"example": 2005})

class ShapContribution(BaseModel):
    feature: str
    feature_label: str
    value: float
    shap_value: float
    importance: float
    effect: str  # "increase_risk" or "decrease_risk"

class PredictionResponse(BaseModel):
    prediction: str
    prediction_code: int
    default_probability: float
    confidence: float
    risk_category: str  # "Low Risk", "Moderate Risk", "High Risk", "Very High Risk"
    processing_time_ms: float

class ExplainResponse(BaseModel):
    prediction: str
    prediction_code: int
    default_probability: float
    confidence: float
    risk_category: str
    processing_time_ms: float
    shap_attributions: List[ShapContribution]
    explanation: str
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    version: str

class ModelInfoResponse(BaseModel):
    model_name: str
    algorithm: str
    training_accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float
    version: str
    num_features: int
    feature_names: List[str]
    confusion_matrix: Dict[str, int]
