"""
Example usage script demonstrating the complete workflow
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    print("="*60)
    print("Heart Disease Prediction - Example Usage")
    print("="*60)
    
    print("\n1. Download Data")
    print("   Command: python src/download_data.py")
    print("   This downloads the Heart Disease UCI dataset")
    
    print("\n2. Run EDA")
    print("   Command: jupyter notebook notebooks/01_eda.ipynb")
    print("   This performs exploratory data analysis")
    
    print("\n3. Train Models")
    print("   Command: python src/train_model.py")
    print("   This trains Logistic Regression and Random Forest models")
    print("   Results are tracked in MLflow")
    
    print("\n4. View MLflow UI")
    print("   Command: mlflow ui --port 10800 --backend-store-uri file://./mlruns")
    print("   Open http://localhost:10800 to view experiments")
    
    print("\n5. Make Predictions (Standalone)")
    print("   Command: python src/predict.py")
    print("   This makes a sample prediction")
    
    print("\n6. Start API Server")
    print("   Command: python -m uvicorn src.api:app --host 0.0.0.0 --port 8000")
    print("   API will be available at http://localhost:8000")
    
    print("\n7. Test API")
    print("   Command: curl http://localhost:8000/health")
    print("   Command: curl -X POST http://localhost:8000/predict -H 'Content-Type: application/json' -d '{...}'")
    
    print("\n8. Run Tests")
    print("   Command: pytest tests/ -v")
    print("   This runs all unit tests")
    
    print("\n9. Build Docker Image")
    print("   Command: docker build -t heart-disease-api:latest -f docker/Dockerfile .")
    
    print("\n10. Run Docker Container")
    print("    Command: docker run -p 8000:8000 heart-disease-api:latest")
    
    print("\n11. Deploy to Kubernetes")
    print("    Command: kubectl apply -f k8s/deployment.yaml")
    
    print("\n" + "="*60)
    print("For detailed instructions, see README.md and DEPLOYMENT.md")
    print("="*60)

if __name__ == "__main__":
    main()

