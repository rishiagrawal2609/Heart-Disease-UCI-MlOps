"""
Unit tests for model training and evaluation
"""

import os
import sys

import numpy as np
import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score


def test_logistic_regression():
    """Test Logistic Regression model"""
    # Create sample data
    X_train = np.random.randn(100, 13)
    y_train = np.random.randint(0, 2, 100)
    X_test = np.random.randn(20, 13)
    y_test = np.random.randint(0, 2, 20)

    # Train model
    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train, y_train)

    # Predict
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    # Check predictions
    assert len(y_pred) == len(y_test)
    assert len(y_proba) == len(y_test)
    assert all(pred in [0, 1] for pred in y_pred)
    assert all(0 <= prob <= 1 for prob in y_proba)

    # Check metrics
    accuracy = accuracy_score(y_test, y_pred)
    assert 0 <= accuracy <= 1


def test_random_forest():
    """Test Random Forest model"""
    # Create sample data
    X_train = np.random.randn(100, 13)
    y_train = np.random.randint(0, 2, 100)
    X_test = np.random.randn(20, 13)
    y_test = np.random.randint(0, 2, 20)

    # Train model
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X_train, y_train)

    # Predict
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    # Check predictions
    assert len(y_pred) == len(y_test)
    assert len(y_proba) == len(y_test)
    assert all(pred in [0, 1] for pred in y_pred)
    assert all(0 <= prob <= 1 for prob in y_proba)

    # Check metrics
    accuracy = accuracy_score(y_test, y_pred)
    assert 0 <= accuracy <= 1


def test_model_predict_proba():
    """Test that models return probability predictions"""
    X = np.random.randn(10, 13)
    y = np.random.randint(0, 2, 10)

    lr_model = LogisticRegression(max_iter=1000, random_state=42)
    lr_model.fit(X, y)
    lr_proba = lr_model.predict_proba(X)

    rf_model = RandomForestClassifier(n_estimators=10, random_state=42)
    rf_model.fit(X, y)
    rf_proba = rf_model.predict_proba(X)

    # Check probability shape and values
    assert lr_proba.shape == (10, 2)
    assert rf_proba.shape == (10, 2)
    assert np.allclose(lr_proba.sum(axis=1), 1.0)
    assert np.allclose(rf_proba.sum(axis=1), 1.0)
