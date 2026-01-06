#!/bin/bash
# Script to verify Jenkins plugins are installed
# Run this inside the Jenkins container after it starts

echo "Checking installed Jenkins plugins..."
ls -la /var/jenkins_home/plugins/ | wc -l
echo "plugins installed"

echo ""
echo "To see all installed plugins, run:"
echo "  docker exec jenkins ls /var/jenkins_home/plugins/"

