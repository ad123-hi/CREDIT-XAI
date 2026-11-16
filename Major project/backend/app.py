import time
import os
import sys
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Ensure the backend directory is in the python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.config import ALLOWED_ORIGINS
from utils.preprocess import load_artifacts
from utils.schemas import HealthResponse
from routes.predict import router as predict_router
import routes.predict as predict_module

app = FastAPI(
    title="Lending Club Credit Risk API",
    description="Production credit risk prediction and model explainability using FastAPI & SHAP",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Startup event to load model and preprocessor once
@app.on_event("startup")
def startup_load_model():
    print("[*] Starting credit risk API services...")
    try:
        model, preprocessor = load_artifacts()
        
        # Inject into router module
        predict_module.model = model
        predict_module.preprocessor = preprocessor
        
        # Pre-initialize SHAP TreeExplainer to cache it for performance
        print("[*] Pre-computing SHAP TreeExplainer to cache in memory...")
        predict_module.shap_explainer = predict_module.get_explainer()
        
        print("[+] Model and preprocessor successfully loaded and cached!")
    except Exception as e:
        print(f"[!] Critical Error loading ML artifacts: {e}", file=sys.stderr)
        raise e

# Secure production exception handler to prevent leaking stack traces
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log error securely (in production, use standard logging)
    print(f"[ERROR] Internal error: {exc}", file=sys.stderr)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred. Please contact the administrator.",
            "error_type": exc.__class__.__name__
        }
    )

# Root Health Check
@app.get("/", response_model=HealthResponse, tags=["Health"])
def health_check():
    """
    API Health Check.
    Returns status and verifies that the ML model is successfully loaded.
    """
    model_loaded = (predict_module.model is not None) and (predict_module.preprocessor is not None)
    return HealthResponse(
        status="healthy" if model_loaded else "degraded",
        model_loaded=model_loaded,
        version="1.0.0"
    )
uvicorn.run(
    "app:app",
    host="0.0.0.0",
    port=int(os.environ.get("PORT", "8000")),
    reload=False,
)

# Include prediction router
app.include_router(predict_router, tags=["Predictions & Explanations"])

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
