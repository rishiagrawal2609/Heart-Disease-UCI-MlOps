#!/bin/bash
# Script to install Jenkins plugins
# This script can be run inside the Jenkins container

PLUGINS_FILE="/usr/share/jenkins/ref/plugins.txt"

if [ -f "$PLUGINS_FILE" ]; then
    echo "Installing plugins from $PLUGINS_FILE..."
    jenkins-plugin-cli --plugin-file "$PLUGINS_FILE"
else
    echo "Plugins file not found: $PLUGINS_FILE"
    exit 1
fi

