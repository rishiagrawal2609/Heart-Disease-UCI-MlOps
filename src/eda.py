"""
Exploratory Data Analysis - Heart Disease Dataset

This script performs comprehensive EDA on the Heart Disease UCI dataset.
Generates visualizations and summary statistics.
"""

import os
import sys
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

warnings.filterwarnings("ignore")

# Add src to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def setup_plotting():
    """Configure matplotlib and seaborn styles"""
    sns.set_style("whitegrid")
    plt.rcParams["figure.figsize"] = (12, 8)
    plt.rcParams["figure.dpi"] = 100


def load_data(data_path):
    """Load the heart disease dataset"""
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Data file not found: {data_path}")

    df = pd.read_csv(data_path)
    print(f"Dataset shape: {df.shape}")
    print(f"\nColumn names: {list(df.columns)}")
    print("\nFirst few rows:")
    print(df.head())
    return df


def basic_info(df):
    """Display basic dataset information"""
    print("\n" + "=" * 50)
    print("Dataset Info:")
    print("=" * 50)
    df.info()
    print("\n" + "=" * 50)
    print("\nMissing Values:")
    missing = df.isnull().sum()
    print(missing)
    if missing.sum() > 0:
        print(f"\nTotal missing values: {missing.sum()}")
    else:
        print("\nNo missing values found!")
    print("\n" + "=" * 50)
    print("\nBasic Statistics:")
    print(df.describe())
    print("\n" + "=" * 50)


def plot_class_distribution(df, output_dir):
    """Plot and save class distribution"""
    plt.figure(figsize=(8, 6))
    target_counts = df["target"].value_counts()
    plt.bar(
        ["No Disease", "Disease"], target_counts.values, color=["skyblue", "salmon"]
    )
    plt.title("Class Distribution (Target Variable)", fontsize=16, fontweight="bold")
    plt.ylabel("Count", fontsize=12)
    plt.xlabel("Heart Disease Status", fontsize=12)
    for i, v in enumerate(target_counts.values):
        plt.text(i, v + 5, str(v), ha="center", fontsize=12)
    plt.tight_layout()

    output_path = os.path.join(output_dir, "class_distribution.png")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"\nSaved class distribution plot to: {output_path}")
    plt.close()

    print(f"\nClass distribution:\n{target_counts}")
    print(f"Class balance ratio: {target_counts[0] / target_counts[1]:.2f}")


def plot_feature_histograms(df, output_dir):
    """Plot histograms for numerical features"""
    numerical_cols = ["age", "trestbps", "chol", "thalach", "oldpeak"]
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    axes = axes.ravel()

    for idx, col in enumerate(numerical_cols):
        axes[idx].hist(
            df[col], bins=30, color="steelblue", edgecolor="black", alpha=0.7
        )
        axes[idx].set_title(
            f"{col.capitalize()} Distribution", fontsize=12, fontweight="bold"
        )
        axes[idx].set_xlabel(col.capitalize())
        axes[idx].set_ylabel("Frequency")
        axes[idx].grid(True, alpha=0.3)

    # Remove empty subplot
    fig.delaxes(axes[5])
    plt.tight_layout()

    output_path = os.path.join(output_dir, "feature_histograms.png")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Saved feature histograms to: {output_path}")
    plt.close()


def plot_correlation_heatmap(df, output_dir):
    """Plot correlation heatmap"""
    plt.figure(figsize=(14, 12))
    correlation_matrix = df.corr()
    mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
    sns.heatmap(
        correlation_matrix,
        mask=mask,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        square=True,
        linewidths=1,
        cbar_kws={"shrink": 0.8},
    )
    plt.title("Feature Correlation Heatmap", fontsize=16, fontweight="bold", pad=20)
    plt.tight_layout()

    output_path = os.path.join(output_dir, "correlation_heatmap.png")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Saved correlation heatmap to: {output_path}")
    plt.close()

    # Top correlations with target
    target_corr = df.corr()["target"].sort_values(ascending=False)
    print("\nTop correlations with target:")
    print(target_corr)


def plot_boxplots_by_target(df, output_dir):
    """Plot box plots for numerical features by target variable"""
    numerical_cols = ["age", "trestbps", "chol", "thalach", "oldpeak"]
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    axes = axes.ravel()

    for idx, col in enumerate(numerical_cols):
        df.boxplot(column=col, by="target", ax=axes[idx])
        axes[idx].set_title(
            f"{col.capitalize()} by Heart Disease", fontsize=12, fontweight="bold"
        )
        axes[idx].set_xlabel("Heart Disease (0=No, 1=Yes)")
        axes[idx].set_ylabel(col.capitalize())
        plt.suptitle("")

    fig.delaxes(axes[5])
    plt.tight_layout()

    output_path = os.path.join(output_dir, "boxplots_by_target.png")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Saved boxplots to: {output_path}")
    plt.close()


def print_summary(df):
    """Print EDA summary"""
    print("\n" + "=" * 50)
    print("EDA Summary")
    print("=" * 50)
    print(
        f"1. Dataset contains {df.shape[0]} samples with {df.shape[1]-1} features and 1 target variable"
    )

    target_counts = df["target"].value_counts()
    print(
        f"2. Class distribution is relatively balanced (ratio: {target_counts[0] / target_counts[1]:.2f})"
    )

    target_corr = df.corr()["target"].abs().sort_values(ascending=False)
    top_features = target_corr[1:4].index.tolist()  # Exclude target itself
    print(f"3. Top features correlated with target: {', '.join(top_features)}")

    missing = df.isnull().sum().sum()
    if missing > 0:
        print(f"4. Missing values need to be handled ({missing} total)")
    else:
        print("4. No missing values found")

    print("5. Feature scaling will be important for distance-based algorithms")
    print("=" * 50)


def main():
    """Main EDA function"""
    # Setup paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    data_path = project_root / "data" / "heart_disease.csv"
    output_dir = project_root / "screenshots"

    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Exploratory Data Analysis - Heart Disease Dataset")
    print("=" * 60)

    # Setup plotting
    setup_plotting()

    # Load data
    print("\n1. Loading data...")
    df = load_data(data_path)

    # Basic information
    print("\n2. Basic dataset information...")
    basic_info(df)

    # Class distribution
    print("\n3. Analyzing class distribution...")
    plot_class_distribution(df, output_dir)

    # Feature histograms
    print("\n4. Plotting feature distributions...")
    plot_feature_histograms(df, output_dir)

    # Correlation heatmap
    print("\n5. Analyzing feature correlations...")
    plot_correlation_heatmap(df, output_dir)

    # Box plots
    print("\n6. Plotting boxplots by target variable...")
    plot_boxplots_by_target(df, output_dir)

    # Summary
    print_summary(df)

    print("\n" + "=" * 60)
    print("EDA completed successfully!")
    print(f"All visualizations saved to: {output_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()
