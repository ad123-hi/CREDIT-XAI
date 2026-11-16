import os

# Base Directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "model")

MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")
PREPROCESSOR_PATH = os.path.join(MODEL_DIR, "preprocessing.pkl")

# CORS Origins
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "credit-xai-frontend.vercel.app"
]

# Model Performance Metrics (Baseline from Notebook)
MODEL_METRICS = {
    "model_name": "Gradient Boosting Classifier",
    "algorithm": "GradientBoostingClassifier",
    "training_accuracy": 0.8790,
    "precision": 0.8400,
    "recall": 0.9371,
    "f1_score": 0.8850,
    "roc_auc": 0.9488,
    "version": "1.0.0",
    "num_features": 27,
    "confusion_matrix": {
        "true_negatives": 1639,
        "false_positives": 358,
        "false_negatives": 126,
        "true_positives": 1877
    }
}

# Features Metadata Dictionary
FEATURES_METADATA = {
    # Applicant Information
    "annual_inc": {
        "name": "annual_inc",
        "datatype": "float",
        "group": "Applicant Information",
        "description": "The self-reported annual income of the borrower.",
        "tooltip": "Enter your annual pre-tax income. Higher income generally translates to lower default risk.",
        "required": True,
        "example": 65000.0,
        "min": 0.0,
        "max": 10000000.0,
        "default": 65000.0
    },
    "emp_length": {
        "name": "emp_length",
        "datatype": "string",
        "group": "Applicant Information",
        "description": "Employment length in years. (Note: Dropped from model due to low class variance but collected for compliance).",
        "tooltip": "Number of years employed. Maps < 1 year to 0, 10+ years to 10.",
        "required": True,
        "example": "10+ years",
        "allowed_values": ["< 1 year", "1 year", "2 years", "3 years", "4 years", "5 years", "6 years", "7 years", "8 years", "9 years", "10+ years"],
        "default": "10+ years"
    },
    "home_ownership": {
        "name": "home_ownership",
        "datatype": "string",
        "group": "Applicant Information",
        "description": "The home ownership status provided by the borrower.",
        "tooltip": "Select your home ownership status. Mortgage is the most common status among low-risk tiers.",
        "required": True,
        "example": "MORTGAGE",
        "allowed_values": ["MORTGAGE", "RENT", "OWN", "ANY", "NONE", "OTHER"],
        "default": "MORTGAGE"
    },
    "verification_status": {
        "name": "verification_status",
        "datatype": "string",
        "group": "Applicant Information",
        "description": "Indicates if the income was verified by Lending Club, not verified, or if the income source was verified.",
        "tooltip": "Lending Club income verification status. Verified income helps establish creditworthiness.",
        "required": True,
        "example": "Not Verified",
        "allowed_values": ["Not Verified", "Source Verified", "Verified"],
        "default": "Not Verified"
    },
    "purpose": {
        "name": "purpose",
        "datatype": "string",
        "group": "Applicant Information",
        "description": "A category provided by the borrower for the loan request.",
        "tooltip": "Select the primary use case of the loan. Debt consolidation and credit card refinancing are very common.",
        "required": True,
        "example": "debt_consolidation",
        "allowed_values": [
            "debt_consolidation", "credit_card", "home_improvement", "other", 
            "major_purchase", "medical", "small_business", "car", 
            "vacation", "moving", "house", "renewable_energy", "wedding"
        ],
        "default": "debt_consolidation"
    },
    "addr_state": {
        "name": "addr_state",
        "datatype": "string",
        "group": "Applicant Information",
        "description": "The state provided by the borrower in the loan application.",
        "tooltip": "Two-letter US state code of residence.",
        "required": True,
        "example": "CA",
        "allowed_values": [
            "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", 
            "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", 
            "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", 
            "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", 
            "WI", "WY"
        ],
        "default": "CA"
    },
    "application_type": {
        "name": "application_type",
        "datatype": "string",
        "group": "Applicant Information",
        "description": "Indicates whether the loan is an individual application or a joint application.",
        "tooltip": "Individual means a single borrower. Joint means two co-borrowers.",
        "required": True,
        "example": "Individual",
        "allowed_values": ["Individual", "Joint App"],
        "default": "Individual"
    },

    # Loan Information
    "loan_amnt": {
        "name": "loan_amnt",
        "datatype": "float",
        "group": "Loan Information",
        "description": "The listed amount of the loan applied for by the borrower.",
        "tooltip": "The total amount of loan requested. Standard ranges are between $500 and $40,000.",
        "required": True,
        "example": 10000.0,
        "min": 500.0,
        "max": 40000.0,
        "default": 10000.0
    },
    "funded_amnt": {
        "name": "funded_amnt",
        "datatype": "float",
        "group": "Loan Information",
        "description": "The total amount committed to that loan at that point in time.",
        "tooltip": "The portion of the requested loan funded by investors. Usually equals the loan amount.",
        "required": True,
        "example": 10000.0,
        "min": 500.0,
        "max": 40000.0,
        "default": 10000.0
    },
    "int_rate": {
        "name": "int_rate",
        "datatype": "float",
        "group": "Loan Information",
        "description": "Interest rate on the loan (%).",
        "tooltip": "The annual interest rate (e.g. 12.5). Higher interest rates correspond to higher risk grades.",
        "required": True,
        "example": 12.0,
        "min": 5.31,
        "max": 30.99,
        "default": 12.0
    },
    "installment": {
        "name": "installment",
        "datatype": "float",
        "group": "Loan Information",
        "description": "The monthly payment owed by the borrower if the loan originates.",
        "tooltip": "The monthly payment amount due (includes principal and interest).",
        "required": True,
        "example": 330.0,
        "min": 4.93,
        "max": 1719.83,
        "default": 330.0
    },
    "term": {
        "name": "term",
        "datatype": "int",
        "group": "Loan Information",
        "description": "The number of payments on the loan. Values are in months.",
        "tooltip": "Choose a 3-year term (36 months) or a 5-year term (60 months). Long terms statistically double risk.",
        "required": True,
        "example": 36,
        "allowed_values": [36, 60],
        "default": 36
    },
    "grade": {
        "name": "grade",
        "datatype": "string",
        "group": "Loan Information",
        "description": "Lending Club assigned loan grade.",
        "tooltip": "Credit risk grade from A (lowest risk) to G (highest risk).",
        "required": True,
        "example": "B",
        "allowed_values": ["A", "B", "C", "D", "E", "F", "G"],
        "default": "B"
    },
    "sub_grade": {
        "name": "sub_grade",
        "datatype": "string",
        "group": "Loan Information",
        "description": "Lending Club assigned loan subgrade.",
        "tooltip": "Refined grade from A1 to G5.",
        "required": True,
        "example": "B1",
        "allowed_values": [f"{g}{i}" for g in "ABCDEFG" for i in "12345"],
        "default": "B1"
    },

    # Credit Profile
    "fico_score": {
        "name": "fico_score",
        "datatype": "float",
        "group": "Credit Profile",
        "description": "Average of borrower's low and high FICO score range.",
        "tooltip": "Borrower's credit score (300 to 850). Values above 700 signify good credit standing.",
        "required": True,
        "example": 700.0,
        "min": 300.0,
        "max": 850.0,
        "default": 700.0
    },
    "dti": {
        "name": "dti",
        "datatype": "float",
        "group": "Credit Profile",
        "description": "Debt-to-income ratio (%).",
        "tooltip": "Ratio of total monthly debt payments (excluding mortgage) divided by monthly income. Lower is safer.",
        "required": True,
        "example": 15.0,
        "min": 0.0,
        "max": 999.0,
        "default": 15.0
    },
    "revol_util": {
        "name": "revol_util",
        "datatype": "float",
        "group": "Credit Profile",
        "description": "Revolving line utilization rate (%).",
        "tooltip": "Percentage of total revolving credit being used. High utilization (e.g. >70%) signals cash flow stress.",
        "required": True,
        "example": 40.0,
        "min": 0.0,
        "max": 150.0,
        "default": 40.0
    },
    "last_pymnt_amnt": {
        "name": "last_pymnt_amnt",
        "datatype": "float",
        "group": "Credit Profile",
        "description": "Last total payment amount received.",
        "tooltip": "The amount paid in the most recent installment. Extremely important indicator of repayment health.",
        "required": True,
        "example": 3000.0,
        "min": 0.0,
        "max": 40000.0,
        "default": 3000.0
    },
    "acc_open_past_24mths": {
        "name": "acc_open_past_24mths",
        "datatype": "int",
        "group": "Credit Profile",
        "description": "Number of personal finance accounts opened in past 24 months.",
        "tooltip": "Accounts opened in the last 2 years. High numbers signal credit-seeking behavior.",
        "required": True,
        "example": 3,
        "min": 0,
        "max": 50,
        "default": 3
    },
    "avg_cur_bal": {
        "name": "avg_cur_bal",
        "datatype": "float",
        "group": "Credit Profile",
        "description": "Average current balance of all accounts.",
        "tooltip": "Average balance across all open credit accounts.",
        "required": True,
        "example": 50000.0,
        "min": 0.0,
        "max": 1000000.0,
        "default": 50000.0
    },
    "bc_open_to_buy": {
        "name": "bc_open_to_buy",
        "datatype": "float",
        "group": "Credit Profile",
        "description": "Total open to buy on revolving bankcard.",
        "tooltip": "The remaining credit limit available to spend on your credit cards.",
        "required": True,
        "example": 10000.0,
        "min": 0.0,
        "max": 500000.0,
        "default": 10000.0
    },
    "bc_util": {
        "name": "bc_util",
        "datatype": "float",
        "group": "Credit Profile",
        "description": "Ratio of total current balance to credit limit for all bankcard accounts (%).",
        "tooltip": "Credit card utilization percentage. Similar to revolving utilization but specific to bankcards.",
        "required": True,
        "example": 50.0,
        "min": 0.0,
        "max": 150.0,
        "default": 50.0
    },
    "mo_sin_old_rev_tl_op": {
        "name": "mo_sin_old_rev_tl_op",
        "datatype": "int",
        "group": "Credit Profile",
        "description": "Months since oldest revolving account opened.",
        "tooltip": "Length of your credit history in months. Longer history is low-risk.",
        "required": True,
        "example": 120,
        "min": 0,
        "max": 1000,
        "default": 120
    },
    "mo_sin_rcnt_rev_tl_op": {
        "name": "mo_sin_rcnt_rev_tl_op",
        "datatype": "int",
        "group": "Credit Profile",
        "description": "Months since most recent revolving account opened.",
        "tooltip": "Months since you last opened a credit line. Opening lines recently increases default probability.",
        "required": True,
        "example": 12,
        "min": 0,
        "max": 500,
        "default": 12
    },
    "mort_acc": {
        "name": "mort_acc",
        "datatype": "int",
        "group": "Credit Profile",
        "description": "Number of mortgage accounts.",
        "tooltip": "Number of active mortgages. Having home equity is correlated with lower default rates.",
        "required": True,
        "example": 2,
        "min": 0,
        "max": 30,
        "default": 2
    },
    "num_actv_rev_tl": {
        "name": "num_actv_rev_tl",
        "datatype": "int",
        "group": "Credit Profile",
        "description": "Number of active revolving trades.",
        "tooltip": "The number of active revolving accounts (like credit cards) that currently have a balance.",
        "required": True,
        "example": 4,
        "min": 0,
        "max": 40,
        "default": 4
    },
    "initial_list_status": {
        "name": "initial_list_status",
        "datatype": "string",
        "group": "Credit Profile",
        "description": "The initial listing status of the loan.",
        "tooltip": "Listing status. w = Whole loan (sold to institutional buyers), f = Fractional loan (split among retail investors).",
        "required": True,
        "example": "w",
        "allowed_values": ["w", "f"],
        "default": "w"
    },
    "earliest_cr_line": {
        "name": "earliest_cr_line",
        "datatype": "int",
        "group": "Credit Profile",
        "description": "The year the borrower's earliest reported credit line was opened.",
        "tooltip": "Select the year your first credit card or loan account was opened.",
        "required": True,
        "example": 2005,
        "min": 1940,
        "max": 2018,
        "default": 2005
    }
}
