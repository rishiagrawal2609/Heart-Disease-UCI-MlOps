# Jenkins Pipeline Setup Guide

This guide explains how to set up and use the Jenkins pipeline for the Heart Disease Prediction MLOps project.

## Files

- `Jenkinsfile` - Declarative pipeline (recommended)
- `Jenkinsfile.groovy` - Scripted pipeline (alternative)

## Prerequisites

### Jenkins Server Requirements

1. **Jenkins Plugins:**
   - Docker Pipeline
   - HTML Publisher
   - Cobertura
   - Email Extension
   - AnsiColor
   - Timestamper

2. **System Requirements:**
   - Docker installed and accessible
   - Python 3.9+ available
   - Git configured
   - Sufficient disk space for builds

3. **Jenkins Agent:**
   - Docker access (user in docker group)
   - Python 3.9+ installed
   - curl, wget available

## Setup Instructions

### 1. Install Required Plugins

In Jenkins:
1. Go to **Manage Jenkins** → **Manage Plugins**
2. Install the following plugins:
   - Docker Pipeline
   - HTML Publisher Plugin
   - Cobertura Plugin
   - Email Extension Plugin
   - AnsiColor Plugin
   - Timestamper Plugin

### 2. Configure Jenkins

1. **Configure Docker:**
   - Ensure Jenkins user can run Docker commands
   ```bash
   sudo usermod -aG docker jenkins
   sudo systemctl restart jenkins
   ```

2. **Configure Email (optional):**
   - Go to **Manage Jenkins** → **Configure System**
   - Set up SMTP server for email notifications

### 3. Create Pipeline Job

1. **New Item:**
   - Click **New Item**
   - Enter job name: `heart-disease-mlops`
   - Select **Pipeline**
   - Click **OK**

2. **Configure Pipeline:**
   - **Definition:** Pipeline script from SCM
   - **SCM:** Git
   - **Repository URL:** Your repository URL
   - **Branch:** `*/main` or `*/master`
   - **Script Path:** `Jenkinsfile`
   - Click **Save**

### 4. Run Pipeline

1. Click **Build Now**
2. Monitor progress in **Build History**
3. Click on build number to see logs

## Pipeline Stages

The pipeline includes the following stages:

1. **Checkout** - Get code from repository
2. **Setup Environment** - Create virtual environment and install dependencies
3. **Code Quality** - Run linters and format checks (parallel)
4. **Download Data** - Download heart disease dataset
5. **Exploratory Data Analysis** - Run EDA and generate visualizations
6. **Train Models** - Train Logistic Regression and Random Forest models
7. **Run Tests** - Execute unit tests with coverage
8. **Build Docker Image** - Build Docker container
9. **Test Docker Container** - Test API endpoints in container
10. **Integration Test** - Test with Prometheus and Grafana

## Artifacts

The pipeline archives:
- EDA visualizations (`screenshots/*.png`)
- Model artifacts (`artifacts/**/*`)
- MLflow runs (`mlruns/**/*`)
- Test coverage reports (HTML)

## Environment Variables

You can configure these in Jenkins:

- `PYTHON_VERSION` - Python version (default: 3.9)
- `DOCKER_IMAGE` - Docker image name (default: heart-disease-api)
- `DOCKER_TAG` - Docker tag (default: BUILD_NUMBER)
- `MLFLOW_PORT` - MLflow UI port (default: 10800)

## Troubleshooting

### Docker Permission Denied

```bash
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
```

### Python Virtual Environment Issues

Ensure Python 3.9+ is available:
```bash
which python3
python3 --version
```

### Tests Failing

Check test logs in Jenkins build output. Common issues:
- Missing dependencies
- Path issues
- Model files not found

### Docker Build Failing

- Check Docker daemon is running
- Verify Dockerfile exists
- Check disk space

## Advanced Configuration

### Multi-Branch Pipeline

For automatic builds on multiple branches:

1. Create **Multibranch Pipeline**
2. Configure branch sources
3. Use same `Jenkinsfile`

### Parallel Execution

The pipeline already runs code quality checks in parallel. You can add more parallel stages:

```groovy
parallel {
    stage('Stage 1') { ... }
    stage('Stage 2') { ... }
}
```

### Deployment Stage

Add deployment after successful tests:

```groovy
stage('Deploy') {
    when {
        branch 'main'
    }
    steps {
        sh 'kubectl apply -f k8s/deployment.yaml'
    }
}
```

## Monitoring

- **Build Status:** Check Jenkins dashboard
- **Test Coverage:** View HTML reports
- **Artifacts:** Download from build page
- **Logs:** View console output

## Best Practices

1. **Use Declarative Pipeline** (`Jenkinsfile`) - More maintainable
2. **Archive Artifacts** - Keep important outputs
3. **Clean Up** - Remove test containers after builds
4. **Email Notifications** - Get notified of failures
5. **Timeouts** - Prevent hanging builds
6. **Retry Logic** - Add retries for flaky tests

## Example Jenkinsfile Usage

The `Jenkinsfile` uses declarative syntax and includes:
- Error handling
- Artifact archiving
- Test coverage reporting
- Docker testing
- Email notifications
- Cleanup steps

## Support

For issues:
1. Check Jenkins console logs
2. Verify all prerequisites are met
3. Review pipeline stage outputs
4. Check Docker and Python versions

