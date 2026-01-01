"""
Standalone prediction script
Useful for testing predictions without starting the API server
"""

import sys
import os
import numpy as np
import mlflow.sklearn
from pathlib import Path

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_preprocessing import HeartDiseasePreprocessor


def load_model_and_preprocessor():
    """Load model and preprocessor"""
    # Try to find latest MLflow model
    model = None
    preprocessor = None

    if os.path.exists("mlruns"):
        try:
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
                    if os.path.exists(model_path):
                        model = mlflow.sklearn.load_model(
                            f"file://{os.path.abspath(model_path)}"
                        )
                        print(f"Loaded model from {model_path}")
        except Exception as e:
            print(f"Error loading MLflow model: {e}")

    # Load preprocessor
    preprocessor_path = "artifacts/preprocessor.pkl"
    if os.path.exists(preprocessor_path):
        preprocessor = HeartDiseasePreprocessor.load(preprocessor_path)
        print(f"Loaded preprocessor from {preprocessor_path}")
    else:
        print("Warning: Preprocessor not found")

    return model, preprocessor


def predict(model, preprocessor, features):
    """Make prediction"""
    # Convert to numpy array
    features_array = np.array([features])

    # Preprocess
    if preprocessor and preprocessor.is_fitted:
        features_processed = preprocessor.transform(features_array)
    else:
        features_processed = features_array

    # Predict
    prediction = model.predict(features_processed)[0]
    probability = model.predict_proba(features_processed)[0][1]

    return int(prediction), float(probability)


if __name__ == "__main__":
    # Example input
    sample_input = {
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

    print("Loading model and preprocessor...")
    model, preprocessor = load_model_and_preprocessor()

    if model is None:
        print("Error: Model not found. Please train the model first.")
        sys.exit(1)

    # Extract features in correct order
    feature_order = [
        "age",
        "sex",
        "cp",
        "trestbps",
        "chol",
        "fbs",
        "restecg",
        "thalach",
        "exang",
        "oldpeak",
        "slope",
        "ca",
        "thal",
    ]
    features = [sample_input[key] for key in feature_order]

    print(f"\nMaking prediction for sample input:")
    for key, value in sample_input.items():
        print(f"  {key}: {value}")

    prediction, probability = predict(model, preprocessor, features)

    print(f"\nPrediction: {'Heart Disease' if prediction == 1 else 'No Heart Disease'}")
    print(f"Probability: {probability:.4f}")
    print(
        f"Confidence: {'High' if probability >= 0.8 else 'Medium' if probability >= 0.6 else 'Low'}"
    )
