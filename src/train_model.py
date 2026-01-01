"""
Model Training Script
Trains Logistic Regression and Random Forest models with MLflow tracking
"""

import mlflow
import mlflow.sklearn
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
)
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys
import os

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_preprocessing import load_and_preprocess_data, HeartDiseasePreprocessor


def evaluate_model(model, X_train, X_test, y_train, y_test, model_name):
    """Evaluate model and return metrics"""
    # Train predictions
    y_train_pred = model.predict(X_train)
    y_train_proba = model.predict_proba(X_train)[:, 1]

    # Test predictions
    y_test_pred = model.predict(X_test)
    y_test_proba = model.predict_proba(X_test)[:, 1]

    # Calculate metrics
    metrics = {
        "train_accuracy": accuracy_score(y_train, y_train_pred),
        "test_accuracy": accuracy_score(y_test, y_test_pred),
        "train_precision": precision_score(y_train, y_train_pred),
        "test_precision": precision_score(y_test, y_test_pred),
        "train_recall": recall_score(y_train, y_train_pred),
        "test_recall": recall_score(y_test, y_test_pred),
        "train_roc_auc": roc_auc_score(y_train, y_train_proba),
        "test_roc_auc": roc_auc_score(y_test, y_test_proba),
    }

    # Cross-validation
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(model, X_train, y_train, cv=cv, scoring="roc_auc")
    metrics["cv_roc_auc_mean"] = cv_scores.mean()
    metrics["cv_roc_auc_std"] = cv_scores.std()

    # Create confusion matrix plot
    cm = confusion_matrix(y_test, y_test_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
    plt.title(f"{model_name} - Confusion Matrix")
    plt.ylabel("True Label")
    plt.xlabel("Predicted Label")

    cm_path = f"artifacts/{model_name}_confusion_matrix.png"
    Path("artifacts").mkdir(exist_ok=True)
    plt.savefig(cm_path)
    plt.close()

    return metrics, cm_path


def train_logistic_regression(X_train, X_test, y_train, y_test, preprocessor):
    """Train Logistic Regression model"""
    with mlflow.start_run(run_name="Logistic_Regression"):
        # Model parameters
        params = {"C": 1.0, "max_iter": 1000, "random_state": 42, "solver": "lbfgs"}

        # Log parameters
        mlflow.log_params(params)

        # Train model
        model = LogisticRegression(**params)
        model.fit(X_train, y_train)

        # Evaluate
        metrics, cm_path = evaluate_model(
            model, X_train, X_test, y_train, y_test, "LogisticRegression"
        )

        # Log metrics
        mlflow.log_metrics(metrics)

        # Log artifacts
        mlflow.log_artifact(cm_path)

        # Log model
        mlflow.sklearn.log_model(model, "model")

        # Save preprocessor
        preprocessor_path = "artifacts/preprocessor.pkl"
        preprocessor.save(preprocessor_path)
        mlflow.log_artifact(preprocessor_path)

        print(f"Logistic Regression - Test ROC-AUC: {metrics['test_roc_auc']:.4f}")

        return model, metrics


def train_random_forest(X_train, X_test, y_train, y_test, preprocessor):
    """Train Random Forest model"""
    with mlflow.start_run(run_name="Random_Forest"):
        # Model parameters
        params = {
            "n_estimators": 100,
            "max_depth": 10,
            "min_samples_split": 5,
            "min_samples_leaf": 2,
            "random_state": 42,
            "n_jobs": -1,
        }

        # Log parameters
        mlflow.log_params(params)

        # Train model
        model = RandomForestClassifier(**params)
        model.fit(X_train, y_train)

        # Evaluate
        metrics, cm_path = evaluate_model(
            model, X_train, X_test, y_train, y_test, "RandomForest"
        )

        # Log metrics
        mlflow.log_metrics(metrics)

        # Log artifacts
        mlflow.log_artifact(cm_path)

        # Log model
        mlflow.sklearn.log_model(model, "model")

        # Save preprocessor
        preprocessor_path = "artifacts/preprocessor.pkl"
        preprocessor.save(preprocessor_path)
        mlflow.log_artifact(preprocessor_path)

        print(f"Random Forest - Test ROC-AUC: {metrics['test_roc_auc']:.4f}")

        return model, metrics


def main():
    """Main training function"""
    # Set MLflow tracking URI
    mlflow.set_tracking_uri("file:./mlruns")
    mlflow.set_experiment("heart_disease_prediction")

    # Load and preprocess data
    print("Loading and preprocessing data...")
    X_train, X_test, y_train, y_test, preprocessor = load_and_preprocess_data()

    print(f"Training set size: {X_train.shape}")
    print(f"Test set size: {X_test.shape}")

    # Train models
    print("\nTraining Logistic Regression...")
    lr_model, lr_metrics = train_logistic_regression(
        X_train, X_test, y_train, y_test, preprocessor
    )

    print("\nTraining Random Forest...")
    rf_model, rf_metrics = train_random_forest(
        X_train, X_test, y_train, y_test, preprocessor
    )

    # Compare models
    print("\n" + "=" * 50)
    print("Model Comparison:")
    print("=" * 50)
    print(f"Logistic Regression - Test ROC-AUC: {lr_metrics['test_roc_auc']:.4f}")
    print(f"Random Forest - Test ROC-AUC: {rf_metrics['test_roc_auc']:.4f}")

    # Select best model based on test ROC-AUC
    if rf_metrics["test_roc_auc"] > lr_metrics["test_roc_auc"]:
        best_model = rf_model
        best_metrics = rf_metrics
        best_model_name = "RandomForest"
        print(f"\nBest model: Random Forest")
    else:
        best_model = lr_model
        best_metrics = lr_metrics
        best_model_name = "LogisticRegression"
        print(f"\nBest model: Logistic Regression")

    # Save best model using MLflow
    with mlflow.start_run(run_name="Best_Model"):
        mlflow.log_params({"model_type": best_model_name})
        mlflow.log_metrics(best_metrics)
        mlflow.sklearn.log_model(best_model, "model")
        preprocessor_path = "artifacts/preprocessor.pkl"
        preprocessor.save(preprocessor_path)
        mlflow.log_artifact(preprocessor_path)

    print("\nTraining completed! Check mlruns/ for experiment tracking.")


if __name__ == "__main__":
    main()
