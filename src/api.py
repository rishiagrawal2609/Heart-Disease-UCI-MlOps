"""
FastAPI Service for Heart Disease Prediction
Exposes /predict endpoint with logging and monitoring
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List

import mlflow.sklearn
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_preprocessing import HeartDiseasePreprocessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("api.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Heart Disease Prediction API",
    description="MLOps Assignment - Heart Disease Prediction Service",
    version="1.0.0",
)

# Global variables for model and preprocessor
model = None
preprocessor = None


class HeartDiseaseInput(BaseModel):
    """Input schema for prediction"""

    age: float = Field(..., ge=0, le=120, description="Age in years")
    sex: int = Field(..., ge=0, le=1, description="Sex (0=female, 1=male)")
    cp: int = Field(..., ge=0, le=3, description="Chest pain type")
    trestbps: float = Field(..., ge=0, description="Resting blood pressure")
    chol: float = Field(..., ge=0, description="Serum cholesterol")
    fbs: int = Field(..., ge=0, le=1, description="Fasting blood sugar > 120 mg/dl")
    restecg: int = Field(
        ..., ge=0, le=2, description="Resting electrocardiographic results"
    )
    thalach: float = Field(..., ge=0, description="Maximum heart rate achieved")
    exang: int = Field(..., ge=0, le=1, description="Exercise induced angina")
    oldpeak: float = Field(..., ge=0, description="ST depression induced by exercise")
    slope: int = Field(..., ge=0, le=2, description="Slope of peak exercise ST segment")
    ca: int = Field(
        ..., ge=0, le=4, description="Number of major vessels colored by flourosopy"
    )
    thal: int = Field(..., ge=0, le=3, description="Thalassemia")

    class Config:
        schema_extra = {
            "example": {
                "age": 63,
                "sex": 1,
                "cp": 3,
                "trestbps": 145,
                "chol": 233,
                "fbs": 1,
                "restecg": 0,
                "thalach": 150,
                "exang": 0,
                "oldpeak": 2.3,
                "slope": 0,
                "ca": 0,
                "thal": 1,
            }
        }


class PredictionResponse(BaseModel):
    """Response schema for prediction"""

    prediction: int = Field(
        ..., description="Predicted class (0=no disease, 1=disease)"
    )
    probability: float = Field(..., description="Probability of heart disease")
    confidence: str = Field(..., description="Confidence level")
    timestamp: str = Field(..., description="Prediction timestamp")


def load_model():
    """Load MLflow model and preprocessor"""
    global model, preprocessor

    try:
        # Try to load from MLflow
        model_path = None

        # Find latest model
        if os.path.exists("mlruns"):
            try:
                import mlflow
                from mlflow.tracking import MlflowClient

                client = MlflowClient()
                experiments = client.search_experiments()
                if experiments:
                    latest_run = client.search_runs(
                        experiment_ids=[experiments[0].experiment_id],
                        max_results=1,
                        order_by=["start_time DESC"],
                    )
                    if latest_run:
                        run_id = latest_run[0].info.run_id
                        model_path = f"mlruns/{experiments[0].experiment_id}/{run_id}/artifacts/model"
            except Exception as e:
                logger.warning(f"Could not use MLflow client: {e}")

        if model_path and os.path.exists(model_path):
            model = mlflow.sklearn.load_model(f"file://{os.path.abspath(model_path)}")
            logger.info(f"Model loaded from {model_path}")
        else:
            # Fallback: try to find any model
            import glob

            model_dirs = []
            for root, dirs, files in os.walk("mlruns"):
                if "model" in dirs:
                    model_dirs.append(os.path.join(root, "model"))

            if model_dirs:
                # Try to load from MLflow format
                for mf in model_dirs:
                    try:
                        model = mlflow.sklearn.load_model(
                            f"file://{os.path.abspath(mf)}"
                        )
                        logger.info(f"Model loaded from {mf}")
                        break
                    except Exception as e:
                        logger.debug(f"Failed to load from {mf}: {e}")
                        continue

        if model is None:
            logger.warning("No model found. API will not be able to serve predictions.")

        # Load preprocessor
        preprocessor_path = os.getenv("PREPROCESSOR_PATH", "artifacts/preprocessor.pkl")
        if os.path.exists(preprocessor_path):
            preprocessor = HeartDiseasePreprocessor.load(preprocessor_path)
            logger.info(f"Preprocessor loaded from {preprocessor_path}")
        else:
            logger.warning("Preprocessor not found, will use default")
            preprocessor = HeartDiseasePreprocessor()

    except Exception as e:
        logger.error(f"Error loading model: {e}", exc_info=True)
        # Don't raise - allow API to start but mark model as unavailable


@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    logger.info("Starting Heart Disease Prediction API...")
    load_model()
    logger.info("API ready to serve predictions")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Heart Disease Prediction API",
        "version": "1.0.0",
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "preprocessor_loaded": preprocessor is not None,
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict(input_data: HeartDiseaseInput):
    """
    Predict heart disease risk

    Returns prediction (0 or 1) and confidence probability
    """
    try:
        # Log request
        logger.info(f"Prediction request received: {input_data.model_dump()}")

        # Convert input to array
        features = np.array(
            [
                [
                    input_data.age,
                    input_data.sex,
                    input_data.cp,
                    input_data.trestbps,
                    input_data.chol,
                    input_data.fbs,
                    input_data.restecg,
                    input_data.thalach,
                    input_data.exang,
                    input_data.oldpeak,
                    input_data.slope,
                    input_data.ca,
                    input_data.thal,
                ]
            ]
        )

        # Preprocess
        if preprocessor and preprocessor.is_fitted:
            features_processed = preprocessor.transform(features)
        else:
            features_processed = features

        # Predict
        if model is None:
            raise HTTPException(status_code=503, detail="Model not loaded")

        prediction = model.predict(features_processed)[0]
        probability = model.predict_proba(features_processed)[0][1]

        # Determine confidence level
        if probability >= 0.8:
            confidence = "High"
        elif probability >= 0.6:
            confidence = "Medium"
        else:
            confidence = "Low"

        response = PredictionResponse(
            prediction=int(prediction),
            probability=float(probability),
            confidence=confidence,
            timestamp=datetime.now().isoformat(),
        )

        logger.info(
            f"Prediction: {prediction}, Probability: {probability:.4f}, Confidence: {confidence}"
        )

        return response

    except Exception as e:
        logger.error(f"Prediction error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.get("/metrics")
async def metrics():
    """Prometheus-compatible metrics endpoint"""
    # Simple metrics for monitoring
    return {
        "requests_total": "N/A",  # Would be tracked in production
        "predictions_total": "N/A",
        "model_version": "1.0.0",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
