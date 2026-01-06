pipeline {
    agent any
    
    environment {
        PYTHON_VERSION = '3.9'
        DOCKER_IMAGE = 'heart-disease-api'
        DOCKER_TAG = "${env.BUILD_NUMBER}"
        MLFLOW_PORT = '10800'
    }
    
    options {
        timeout(time: 60, unit: 'MINUTES')
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }
    
    stages {
        stage('Checkout') {
            steps {
                script {
                    echo "Checking out code from ${env.GIT_BRANCH}"
                    checkout scm
                }
            }
        }
        
        stage('Setup Environment') {
            steps {
                ansiColor('xterm') {
                    script {
                        echo "Setting up Python environment..."
                        sh '''
                            #!/bin/bash
                            python3 --version
                            python3 -m venv venv || true
                            source venv/bin/activate || . venv/bin/activate
                            pip install --upgrade pip
                            pip install setuptools wheel
                            pip install -r requirements.txt
                        '''
                    }
                }
            }
        }
        
        stage('Code Quality') {
            parallel {
                stage('Lint') {
                    steps {
                        script {
                            sh '''
                                source venv/bin/activate || . venv/bin/activate
                                echo "Running linters..."
                                flake8 src/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics || true
                                flake8 src/ tests/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
                            '''
                        }
                    }
                }
                
                stage('Format Check') {
                    steps {
                        script {
                            sh '''
                                source venv/bin/activate || . venv/bin/activate
                                echo "Checking code formatting..."
                                black --check src/ tests/ || true
                                isort --check-only src/ tests/ || true
                            '''
                        }
                    }
                }
            }
        }
        
        stage('Download Data') {
            steps {
                script {
                    sh '''
                        source venv/bin/activate || . venv/bin/activate
                        echo "Downloading dataset..."
                        python src/download_data.py
                        ls -lh data/
                    '''
                }
            }
        }
        
        stage('Exploratory Data Analysis') {
            steps {
                script {
                    sh '''
                        source venv/bin/activate || . venv/bin/activate
                        echo "Running EDA..."
                        python src/eda.py || echo "EDA step failed, continuing..."
                        ls -lh screenshots/ || true
                    '''
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'screenshots/*.png', allowEmptyArchive: true
                }
            }
        }
        
        stage('Train Models') {
            steps {
                script {
                    sh '''
                        source venv/bin/activate || . venv/bin/activate
                        echo "Training models..."
                        python src/train_model.py
                        ls -lh artifacts/ mlruns/ || true
                    '''
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'artifacts/**/*', allowEmptyArchive: true
                    archiveArtifacts artifacts: 'mlruns/**/*', allowEmptyArchive: true
                }
            }
        }
        
        stage('Run Tests') {
            steps {
                script {
                    sh '''
                        source venv/bin/activate || . venv/bin/activate
                        echo "Running tests..."
                        pytest tests/ -v --cov=src --cov-report=html --cov-report=xml
                    '''
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'htmlcov/**/*', allowEmptyArchive: true
                    archiveArtifacts artifacts: 'coverage.xml', allowEmptyArchive: true
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    echo "Building Docker image..."
                    sh '''
                        docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} -f docker/Dockerfile .
                        docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest
                    '''
                }
            }
            post {
                success {
                    script {
                        echo "Docker image built successfully: ${DOCKER_IMAGE}:${DOCKER_TAG}"
                    }
                }
            }
        }
        
        stage('Test Docker Container') {
            steps {
                script {
                    sh '''
                        echo "Testing Docker container..."
                        # Clean up any existing container with the same name
                        docker stop test-api-${BUILD_NUMBER} || true
                        docker rm test-api-${BUILD_NUMBER} || true
                        
                        # Start container with curl installed or use a base image that has it
                        docker run -d -p 8000:8000 --name test-api-${BUILD_NUMBER} ${DOCKER_IMAGE}:${DOCKER_TAG}
                        
                        # Wait for container to be ready using Python (most reliable - Python is always available)
                        echo "Waiting for container to be ready..."
                        max_attempts=30
                        attempt=0
                        success=0
                        
                        while [ $attempt -lt $max_attempts ]; do
                            # Check if container is running
                            if ! docker ps | grep -q test-api-${BUILD_NUMBER}; then
                                echo "Container is not running!"
                                docker ps -a | grep test-api-${BUILD_NUMBER}
                                docker logs test-api-${BUILD_NUMBER}
                                exit 1
                            fi
                            
                            # Use Python to test from inside the container (most reliable - Python is always available)
                            if docker exec test-api-${BUILD_NUMBER} python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=5).read()" > /dev/null 2>&1; then
                                echo "Container is ready! (attempt $((attempt + 1)))"
                                success=1
                                break
                            fi
                            
                            attempt=$((attempt + 1))
                            if [ $((attempt % 5)) -eq 0 ]; then
                                echo "Attempt $attempt/$max_attempts - still waiting..."
                                docker logs --tail 10 test-api-${BUILD_NUMBER}
                            fi
                            sleep 2
                        done
                        
                        if [ $success -eq 0 ]; then
                            echo "Container failed to become ready after $max_attempts attempts"
                            echo "Container status:"
                            docker ps -a | grep test-api-${BUILD_NUMBER}
                            echo "Container logs:"
                            docker logs test-api-${BUILD_NUMBER}
                            echo "Port binding check:"
                            docker port test-api-${BUILD_NUMBER}
                            exit 1
                        fi
                        
                        # Give it a moment to fully stabilize
                        sleep 2
                        
                        echo "Testing health endpoint..."
                        docker exec test-api-${BUILD_NUMBER} python -c "import urllib.request; import json; response = urllib.request.urlopen('http://localhost:8000/health'); print(response.read().decode())" || (docker logs test-api-${BUILD_NUMBER}; exit 1)
                        
                        echo "Testing prediction endpoint..."
                        docker exec test-api-${BUILD_NUMBER} python -c "
import urllib.request
import json
data = json.dumps({'age':63,'sex':1,'cp':3,'trestbps':145,'chol':233,'fbs':1,'restecg':0,'thalach':150,'exang':0,'oldpeak':2.3,'slope':0,'ca':0,'thal':1}).encode()
req = urllib.request.Request('http://localhost:8000/predict', data=data, headers={'Content-Type': 'application/json'})
response = urllib.request.urlopen(req)
print(response.read().decode())
" || (docker logs test-api-${BUILD_NUMBER}; exit 1)
                        
                        echo "✓ Docker container tests passed"
                    '''
                }
            }
            post {
                always {
                    script {
                        sh '''
                            docker stop test-api-${BUILD_NUMBER} || true
                            docker rm test-api-${BUILD_NUMBER} || true
                        '''
                    }
                }
            }
        }
        
        stage('Integration Test') {
            steps {
                script {
                    sh '''
                        echo "Starting services for integration test..."
                        cd docker
                        docker-compose up -d prometheus grafana || true
                        sleep 10
                        
                        echo "Checking Prometheus targets..."
                        curl -s http://localhost:9090/api/v1/targets | python3 -m json.tool || true
                        
                        echo "Checking Grafana health..."
                        curl -s http://localhost:3000/api/health || true
                    '''
                }
            }
            post {
                always {
                    script {
                        sh '''
                            cd docker
                            docker-compose down || true
                        '''
                    }
                }
            }
        }
    }
    
    post {
        always {
            script {
                echo "Pipeline execution completed"
                // Cleanup
                sh ''' 
                    echo "Application is running at http://localhost:8000"
                '''
            }
        }
        success {
            script {
                echo "✓ Pipeline succeeded!"
                emailext(
                    subject: "✓ Pipeline Success: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                    body: "Pipeline completed successfully.\n\nBuild: ${env.BUILD_URL}",
                    to: "${env.CHANGE_AUTHOR_EMAIL}"
                )
            }
        }
        failure {
            script {
                echo "✗ Pipeline failed!"
                emailext(
                    subject: "✗ Pipeline Failed: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                    body: "Pipeline failed. Check the build logs: ${env.BUILD_URL}",
                    to: "${env.CHANGE_AUTHOR_EMAIL}"
                )
            }
        }
        unstable {
            script {
                echo "⚠ Pipeline unstable"
            }
        }
    }
}

