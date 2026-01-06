# Custom Jenkins image with Docker and Python pre-installed
FROM jenkins/jenkins:lts

USER root

# Install Docker CLI and dependencies
RUN apt-get update && \
    apt-get install -y \
    docker.io \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Docker Compose
RUN curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && \
    chmod +x /usr/local/bin/docker-compose

# Add jenkins user to docker group
RUN usermod -aG docker jenkins

# Copy plugins list (build context is project root, so path is docker/jenkins/plugins.txt)
COPY docker/jenkins/plugins.txt /usr/share/jenkins/ref/plugins.txt

USER jenkins

# Plugins will be installed automatically on first startup from plugins.txt

