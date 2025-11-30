"""
Data Acquisition Script
Downloads the Heart Disease UCI dataset from UCI Machine Learning Repository
"""
import os
import urllib.request
import pandas as pd
from pathlib import Path

def download_heart_disease_dataset(data_dir="data"):
    """
    Download Heart Disease UCI dataset from UCI ML Repository
    """
    # Create data directory if it doesn't exist
    Path(data_dir).mkdir(parents=True, exist_ok=True)
    
    # UCI Heart Disease dataset URL
    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data"
    
    # Column names based on UCI dataset description
    column_names = [
        'age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg',
        'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal', 'target'
    ]
    
    output_path = os.path.join(data_dir, "heart_disease.csv")
    
    print(f"Downloading Heart Disease dataset from UCI...")
    print(f"URL: {url}")
    
    try:
        # Download the file
        urllib.request.urlretrieve(url, output_path)
        print(f"Downloaded to: {output_path}")
        
        # Read and clean the data
        df = pd.read_csv(output_path, names=column_names, na_values='?')
        
        # Convert target to binary (0 = no disease, 1 = disease)
        # Original dataset has 0-4, we'll convert >0 to 1
        df['target'] = (df['target'] > 0).astype(int)
        
        # Save cleaned version
        df.to_csv(output_path, index=False)
        print(f"Dataset saved with {len(df)} rows and {len(df.columns)} columns")
        print(f"Target distribution:\n{df['target'].value_counts()}")
        
        return output_path
        
    except Exception as e:
        print(f"Error downloading dataset: {e}")
        print("Trying alternative: using Kaggle dataset URL...")
        
        # Alternative: Try direct download from a mirror
        try:
            # Using a more reliable source
            alt_url = "https://raw.githubusercontent.com/plotly/datasets/master/heart.csv"
            urllib.request.urlretrieve(alt_url, output_path)
            df = pd.read_csv(output_path)
            if 'target' not in df.columns:
                # Rename if needed
                if 'target' in df.columns or 'condition' in df.columns:
                    pass
                else:
                    # Assume last column is target
                    df.columns = list(df.columns[:-1]) + ['target']
            df.to_csv(output_path, index=False)
            print(f"Downloaded alternative dataset with {len(df)} rows")
            return output_path
        except Exception as e2:
            print(f"Alternative download also failed: {e2}")
            raise

if __name__ == "__main__":
    download_heart_disease_dataset()

