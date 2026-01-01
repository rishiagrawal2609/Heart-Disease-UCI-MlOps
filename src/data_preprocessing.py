"""
Data Preprocessing Pipeline
Handles missing values, encoding, and feature scaling
"""

import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler


class HeartDiseasePreprocessor:
    """Preprocessing pipeline for Heart Disease dataset"""

    def __init__(self):
        self.scaler = StandardScaler()
        self.imputer = SimpleImputer(strategy="median")
        self.is_fitted = False

    def fit(self, X):
        """Fit the preprocessor on training data"""
        # Handle missing values
        X_imputed = self.imputer.fit_transform(X)

        # Scale features
        self.scaler.fit(X_imputed)

        self.is_fitted = True
        return self

    def transform(self, X):
        """Transform data using fitted preprocessor"""
        if not self.is_fitted:
            raise ValueError("Preprocessor must be fitted before transform")

        # Impute missing values
        X_imputed = self.imputer.transform(X)

        # Scale features
        X_scaled = self.scaler.transform(X_imputed)

        return X_scaled

    def fit_transform(self, X):
        """Fit and transform in one step"""
        return self.fit(X).transform(X)

    def save(self, filepath):
        """Save preprocessor to disk"""
        with open(filepath, "wb") as f:
            pickle.dump(
                {
                    "scaler": self.scaler,
                    "imputer": self.imputer,
                    "is_fitted": self.is_fitted,
                },
                f,
            )

    @classmethod
    def load(cls, filepath):
        """Load preprocessor from disk"""
        with open(filepath, "rb") as f:
            data = pickle.load(f)

        preprocessor = cls()
        preprocessor.scaler = data["scaler"]
        preprocessor.imputer = data["imputer"]
        preprocessor.is_fitted = data["is_fitted"]

        return preprocessor


def load_and_preprocess_data(
    data_path="data/heart_disease.csv", test_size=0.2, random_state=42
):
    """
    Load and preprocess the heart disease dataset

    Returns:
        X_train, X_test, y_train, y_test, preprocessor
    """
    from sklearn.model_selection import train_test_split

    # Load data
    df = pd.read_csv(data_path)

    # Separate features and target
    X = df.drop("target", axis=1)
    y = df["target"]

    # Check if we can use stratified split (need at least 2 samples per class)
    # in each split
    min_samples_per_class = min(y.value_counts())
    min_test_samples = int(len(df) * test_size)
    min_train_samples = len(df) - min_test_samples

    # Use stratify only if we have enough samples in each class for both splits
    use_stratify = (
        min_samples_per_class >= 2 and min_test_samples >= 2 and min_train_samples >= 2
    )

    # Split data
    split_kwargs = {
        "test_size": test_size,
        "random_state": random_state,
    }
    if use_stratify:
        split_kwargs["stratify"] = y

    X_train, X_test, y_train, y_test = train_test_split(X, y, **split_kwargs)

    # Fit preprocessor on training data
    preprocessor = HeartDiseasePreprocessor()
    X_train_processed = preprocessor.fit_transform(X_train)
    X_test_processed = preprocessor.transform(X_test)

    return (
        X_train_processed,
        X_test_processed,
        y_train.values,
        y_test.values,
        preprocessor,
    )
