# CI/CD Pipeline Documentation

This directory contains GitHub Actions workflows for automated CI/CD of the Heart Disease Prediction MLOps project.

## Workflows

### 1. CI/CD Pipeline (`ci-cd.yml`)

The main continuous integration and continuous deployment pipeline that runs on every push and pull request.

#### Jobs Overview

1. **code-quality** - Code quality checks
   - Black formatting check
   - isort import sorting check
   - Flake8 linting

2. **unit-tests** - Unit testing
   - Pytest with coverage
   - Codecov integration
   - HTML coverage reports

3. **data-validation** - Data validation
   - Downloads dataset
   - Validates data structure
   - Checks for missing values

4. **model-training** - Model training
   - Trains Logistic Regression and Random Forest
   - MLflow experiment tracking
   - Artifact validation and upload

5. **docker-build-test** - Docker build and test
   - Builds Docker image
   - Tests container health
   - Tests prediction endpoint
   - Saves Docker image artifact

6. **e2e-pipeline** - End-to-end pipeline test
   - Runs complete pipeline script
   - Validates full workflow

7. **pipeline-summary** - Pipeline summary
   - Generates summary of all jobs
   - Provides status overview

#### Triggers

- Push to `main`, `master`, or `develop` branches
- Pull requests to `main`, `master`, or `develop` branches
- Manual trigger via `workflow_dispatch`

#### Artifacts

The workflow generates and stores:
- Coverage reports (30 days retention)
- Model artifacts (30 days retention)
- Training logs (7 days retention)
- Docker images (7 days retention)
- Pipeline logs (7 days retention)

### 2. Deployment Pipeline (`deploy.yml`)

Deployment workflow that validates Kubernetes manifests and Helm charts.

#### Triggers

- Automatically after successful CI/CD pipeline completion
- Manual trigger with environment selection (staging/production)

#### Features

- Downloads Docker image from CI/CD pipeline
- Validates Kubernetes deployment manifests
- Validates Helm charts
- Generates deployment summary

## Usage

### Running the Pipeline Locally

While you can't run GitHub Actions locally, you can simulate the pipeline using the Makefile:

```bash
# Install dependencies
make install

# Run linting
make lint

# Format code
make format

# Run tests
make test

# Train models
make train

# Build Docker image
make docker-build

# Run Docker container
make docker-run
```

### Viewing Pipeline Results

1. Go to the **Actions** tab in your GitHub repository
2. Click on a workflow run to see detailed logs
3. Download artifacts from the workflow run page
4. Check the summary section for job status overview

### Troubleshooting

#### Pipeline Fails on Linting

- Run `make format` locally to auto-fix formatting issues
- Check Flake8 errors and fix them manually

#### Pipeline Fails on Tests

- Run `pytest tests/ -v` locally to see test failures
- Check test coverage and add missing tests

#### Pipeline Fails on Model Training

- Ensure dataset is downloaded successfully
- Check MLflow tracking URI configuration
- Verify sufficient disk space for artifacts

#### Docker Build Fails

- Ensure all dependencies are in `requirements.txt`
- Check that model artifacts exist before building
- Verify Dockerfile paths are correct

#### Deployment Fails

- Check Kubernetes manifest syntax
- Verify Helm chart structure
- Ensure kubectl/helm are properly configured (if applicable)

## Best Practices

1. **Always run tests locally** before pushing
2. **Fix linting issues** before committing
3. **Keep artifacts small** - use `.gitignore` for large files
4. **Monitor pipeline duration** - optimize slow jobs
5. **Review logs** - check for warnings and errors
6. **Test Docker builds** locally before pushing

## Workflow Status Badge

Add this to your README.md to show pipeline status:

```markdown
![CI/CD Pipeline](https://github.com/YOUR_USERNAME/YOUR_REPO/workflows/CI/CD%20Pipeline/badge.svg)
```

Replace `YOUR_USERNAME` and `YOUR_REPO` with your actual GitHub username and repository name.

