// Alternative Jenkinsfile using scripted pipeline syntax
// This is a more flexible version if you need more control

node {
    def pythonEnv = "venv"
    def dockerImage = "heart-disease-api"
    def dockerTag = "${env.BUILD_NUMBER}"
    
    try {
        stage('Checkout') {
            checkout scm
        }
        
        stage('Setup') {
            sh '''
                python3 -m venv venv || true
                source venv/bin/activate || . venv/bin/activate
                pip install --upgrade pip
                pip install setuptools wheel
                pip install -r requirements.txt
            '''
        }
        
        stage('Code Quality') {
            sh '''
                source venv/bin/activate || . venv/bin/activate
                flake8 src/ tests/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
            '''
        }
        
        stage('Download Data') {
            sh '''
                source venv/bin/activate || . venv/bin/activate
                python src/download_data.py
            '''
        }
        
        stage('EDA') {
            sh '''
                source venv/bin/activate || . venv/bin/activate
                python src/eda.py || echo "EDA failed, continuing..."
            '''
            archiveArtifacts 'screenshots/*.png'
        }
        
        stage('Train') {
            sh '''
                source venv/bin/activate || . venv/bin/activate
                python src/train_model.py
            '''
            archiveArtifacts 'artifacts/**/*'
            archiveArtifacts 'mlruns/**/*'
        }
        
        stage('Test') {
            sh '''
                source venv/bin/activate || . venv/bin/activate
                pytest tests/ -v --cov=src --cov-report=html --cov-report=xml
            '''
            archiveArtifacts 'htmlcov/**/*'
        }
        
        stage('Build Docker') {
            sh """
                docker build -t ${dockerImage}:${dockerTag} -f docker/Dockerfile .
                docker tag ${dockerImage}:${dockerTag} ${dockerImage}:latest
            """
        }
        
        stage('Test Docker') {
            sh """
                docker run -d -p 8000:8000 --name test-api-${BUILD_NUMBER} ${dockerImage}:${dockerTag}
                sleep 15
                curl -f http://localhost:8000/health
                curl -X POST http://localhost:8000/predict \\
                  -H "Content-Type: application/json" \\
                  -d '{"age":63,"sex":1,"cp":3,"trestbps":145,"chol":233,"fbs":1,"restecg":0,"thalach":150,"exang":0,"oldpeak":2.3,"slope":0,"ca":0,"thal":1}'
            """
        }
        
        stage('Cleanup') {
            sh """
                docker stop test-api-${BUILD_NUMBER} || true
                docker rm test-api-${BUILD_NUMBER} || true
            """
        }
        
    } catch (Exception e) {
        currentBuild.result = 'FAILURE'
        throw e
    } finally {
        // Always cleanup
        sh """
            docker ps -a | grep test-api | awk '{print \$1}' | xargs -r docker rm -f || true
        """
    }
}

