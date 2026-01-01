"""
Unit tests for data preprocessing
"""

import os
import sys

import numpy as np
import pandas as pd
import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from data_preprocessing import HeartDiseasePreprocessor, load_and_preprocess_data


def test_preprocessor_initialization():
    """Test preprocessor initialization"""
    preprocessor = HeartDiseasePreprocessor()
    assert preprocessor.is_fitted == False
    assert preprocessor.scaler is not None
    assert preprocessor.imputer is not None


def test_preprocessor_fit_transform():
    """Test preprocessor fit and transform"""
    preprocessor = HeartDiseasePreprocessor()

    # Create sample data
    X = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]])

    # Fit and transform
    X_transformed = preprocessor.fit_transform(X)

    assert preprocessor.is_fitted == True
    assert X_transformed.shape == X.shape
    assert not np.isnan(X_transformed).any()


def test_preprocessor_missing_values():
    """Test preprocessor handles missing values"""
    preprocessor = HeartDiseasePreprocessor()

    # Create data with missing values
    X = np.array([[1.0, 2.0, np.nan], [4.0, np.nan, 6.0], [7.0, 8.0, 9.0]])

    X_transformed = preprocessor.fit_transform(X)

    assert not np.isnan(X_transformed).any()
    assert X_transformed.shape == X.shape


def test_preprocessor_save_load(tmp_path):
    """Test preprocessor save and load"""
    preprocessor = HeartDiseasePreprocessor()
    X = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    preprocessor.fit_transform(X)

    # Save
    filepath = tmp_path / "preprocessor.pkl"
    preprocessor.save(str(filepath))

    # Load
    loaded_preprocessor = HeartDiseasePreprocessor.load(str(filepath))

    assert loaded_preprocessor.is_fitted == True
    assert loaded_preprocessor.scaler is not None
    assert loaded_preprocessor.imputer is not None


def test_load_and_preprocess_data(tmp_path):
    """Test data loading and preprocessing"""
    # Create sample dataset with enough samples for stratified split
    # Need at least 2 samples per class in each split
    data = {
        "age": [63, 37, 41, 56, 45, 50, 60, 35],
        "sex": [1, 1, 0, 1, 0, 1, 0, 1],
        "cp": [3, 2, 1, 3, 2, 1, 0, 2],
        "trestbps": [145, 130, 130, 140, 120, 135, 150, 125],
        "chol": [233, 250, 204, 220, 200, 240, 260, 210],
        "fbs": [1, 0, 0, 1, 0, 0, 1, 0],
        "restecg": [0, 1, 0, 0, 1, 0, 1, 0],
        "thalach": [150, 187, 172, 160, 180, 170, 155, 175],
        "exang": [0, 0, 0, 1, 0, 0, 1, 0],
        "oldpeak": [2.3, 3.5, 1.4, 2.0, 1.0, 1.5, 3.0, 1.2],
        "slope": [0, 0, 2, 1, 2, 1, 0, 2],
        "ca": [0, 0, 0, 1, 0, 0, 2, 0],
        "thal": [1, 3, 3, 2, 3, 2, 1, 3],
        "target": [1, 0, 0, 1, 0, 1, 0, 0],  # 4 class 0, 4 class 1
    }
    df = pd.DataFrame(data)

    # Save to temporary file
    data_path = tmp_path / "test_data.csv"
    df.to_csv(data_path, index=False)

    # Load and preprocess
    X_train, X_test, y_train, y_test, preprocessor = load_and_preprocess_data(
        str(data_path), test_size=0.25, random_state=42
    )

    assert X_train.shape[0] + X_test.shape[0] == len(df)
    assert X_train.shape[1] == len(df.columns) - 1  # Exclude target
    assert len(y_train) == X_train.shape[0]
    assert len(y_test) == X_test.shape[0]
    assert preprocessor.is_fitted == True
