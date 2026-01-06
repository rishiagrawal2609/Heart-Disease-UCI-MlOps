# Jenkins Server Setup

This directory contains the Docker configuration for running Jenkins server.

## Quick Start

**Start Jenkins:**
```bash
make jenkins
```

**Get initial admin password:**
```bash
make jenkins-password
```

**View logs:**
```bash
make jenkins-logs
```

**Check installed plugins:**
```bash
make jenkins-plugins
```

**Stop Jenkins:**
```bash
make jenkins-down
```

## Plugin Installation

All required plugins are automatically installed on first startup from `plugins.txt`. The plugins include:

- **Pipeline plugins**: workflow-aggregator, pipeline-stage-view, blueocean
- **Docker plugins**: docker-workflow, docker-plugin
- **Code quality**: htmlpublisher, cobertura
- **Notifications**: email-ext
- **UI enhancements**: ansicolor, timestamper
- **Git integration**: git, github, github-branch-source
- **Security**: credentials-binding, matrix-auth, role-strategy
- **Pipeline utilities**: All pipeline-* plugins

Plugins are installed automatically when Jenkins starts for the first time. You can verify installation by:
1. Going to **Manage Jenkins** → **Manage Plugins** → **Installed**
2. Running `make jenkins-plugins` to see plugin count

## Access Jenkins

1. **Open Jenkins UI:**
   - URL: http://localhost:8080

2. **First-time setup:**
   - Get the initial admin password: `make jenkins-password`
   - Enter the password in Jenkins UI
   - Install suggested plugins (or select specific ones)
   - Create admin user
   - Start using Jenkins

## Features

The Jenkins server includes:
- **Docker support** - Can build and run Docker containers
- **Python 3.9+** - Pre-installed for running pipelines
- **Docker Compose** - Available for multi-container setups
- **Git** - For source control
- **Pre-installed plugins** - Pipeline, Docker, HTML Publisher, etc.

## Configuration

### Jenkins Home

Jenkins data is persisted in a Docker volume:
- Volume name: `jenkins_home`
- Location: `/var/jenkins_home` in container
- Persists across container restarts

### Workspace

The project code is mounted at `/workspace` in the Jenkins container, so pipelines can access:
- Source code
- Scripts
- Configuration files

### Docker Access

Jenkins has access to the host Docker daemon via:
- Docker socket: `/var/run/docker.sock`
- Jenkins user is in the docker group

## Setting Up Pipeline

1. **Create Pipeline Job:**
   - New Item → Pipeline
   - Name: `heart-disease-mlops`

2. **Configure Pipeline:**
   - Definition: Pipeline script from SCM
   - SCM: Git
   - Repository URL: Your repo URL
   - Script Path: `Jenkinsfile`

3. **Run Pipeline:**
   - Click "Build Now"
   - Monitor progress

## Troubleshooting

### Jenkins won't start

```bash
# Check logs
make jenkins-logs

# Check if port 8080 is in use
lsof -i :8080
```

### Can't access Jenkins

1. Wait 1-2 minutes for Jenkins to fully start
2. Check container is running: `docker ps | grep jenkins`
3. Check logs: `make jenkins-logs`

### Docker commands fail in pipeline

Ensure Jenkins container has Docker access:
```bash
docker exec jenkins docker ps
```

If it fails, restart Jenkins:
```bash
make jenkins-down
make jenkins
```

### Plugins not installing

Plugins are installed on first startup. If they don't install:
1. Go to Jenkins UI → Manage Jenkins → Manage Plugins
2. Install plugins manually
3. Restart Jenkins

## Manual Setup

If you prefer to set up manually:

```bash
cd docker
docker-compose -f docker-compose.jenkins.yml up -d
```

## Cleanup

To completely remove Jenkins (including data):

```bash
make jenkins-down
docker volume rm docker_jenkins_home
```

## Ports

- **8080** - Jenkins web UI
- **50000** - Jenkins agent communication

## Environment Variables

- `JENKINS_OPTS` - Jenkins startup options
- `JAVA_OPTS` - JVM options (memory settings)
- `DOCKER_HOST` - Docker daemon socket

