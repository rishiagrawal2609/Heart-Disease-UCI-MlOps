# Custom Jenkins image with Docker and Python pre-installed
FROM jenkins/jenkins:lts

USER root

# Install Docker CLI and dependencies
RUN apt-get update && \
    apt-get install -y \
    docker.io \
    curl \
    wget \
    git \
    unzip \
    build-essential \
    zlib1g-dev \
    libncurses5-dev \
    libgdbm-dev \
    libnss3-dev \
    libssl-dev \
    libreadline-dev \
    libffi-dev \
    libsqlite3-dev \
    libbz2-dev \
    liblzma-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python 3.9 from source for compatibility with requirements.txt
RUN cd /tmp && \
    wget https://www.python.org/ftp/python/3.9.20/Python-3.9.20.tgz && \
    tar -xzf Python-3.9.20.tgz && \
    cd Python-3.9.20 && \
    ./configure --prefix=/usr/local --enable-optimizations --with-ensurepip=yes && \
    make -j$(nproc) && \
    make altinstall && \
    cd / && \
    rm -rf /tmp/Python-3.9.20*

# Set Python 3.9 as the default python3
RUN update-alternatives --install /usr/bin/python3 python3 /usr/local/bin/python3.9 1 && \
    update-alternatives --install /usr/bin/pip3 pip3 /usr/local/bin/pip3.9 1

# Install Docker Compose
RUN curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && \
    chmod +x /usr/local/bin/docker-compose

# Add jenkins user to docker group
RUN usermod -aG docker jenkins

# Copy plugins list (build context is project root, so path is docker/jenkins/plugins.txt)
COPY docker/jenkins/plugins.txt /usr/share/jenkins/ref/plugins.txt

USER jenkins

# Plugins will be automatically installed on first Jenkins startup
# The plugins.txt file in /usr/share/jenkins/ref/ is automatically processed by Jenkins

