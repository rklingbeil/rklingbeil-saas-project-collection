# SaaS Case Analysis Application Deployment Documentation

## Overview
This document provides comprehensive documentation for the SaaS Case Analysis application deployment on EC2. It includes details about the configuration, troubleshooting steps taken, and maintenance procedures.

## Deployment Status
- **Status**: Successfully deployed
- **Access URL**: http://18.226.96.42
- **Application Port**: 5001
- **Web Server**: Nginx (proxying to port 5001) 

## Configuration Details

### Application Configuration
The application is a Flask-based API that provides legal case analysis functionality. Due to compatibility issues with the original implementation, we created a simplified version that provides basic functionality:

- The application is located at `/opt/saas-case-analysis/SaasDeployClean/`
- The main application file is `app.py`
- The application runs on port 5001
- The application is configured to run as a systemd service named `saas-application.service`

### Nginx Configuration
Nginx is configured to proxy requests to the Flask application:

- Configuration file: `/etc/nginx/conf.d/saas-app.conf`
- Nginx listens on port 80 (HTTP)
- All requests are proxied to `http://localhost:5001`
- Static files are served from `/opt/saas-case-analysis/SaasDeployClean/static/`

### System Service Configuration
The application runs as a systemd service:

- Service file: `/etc/systemd/system/saas-application.service`
- The service runs as the `ec2-user` user
- The service automatically restarts if it fails
- The service is enabled to start on system boot

## Troubleshooting and Fixes

### Huggingface-Hub Compatibility Issue
We encountered an issue with the huggingface-hub library. The application was trying to use the `cached_download` function which was renamed in newer versions of the library.

**Solution**: We installed huggingface-hub version 0.12.0 which includes the `cached_download` function:
sudo -u root bash -c 'source /opt/saas-case-analysis/venv/bin/activate && pip uninstall -y huggingface-hub && pip install huggingface-hub==0.12.0'

### Model Path Issue
The application was configured to use a local Mistral model at `/Users/Rick/LegalCaseLLMProject/models/mistral`, which doesn't exist on the EC2 instance.

**Solution**: We simplified the application to remove the dependency on the Mistral model, as the actual implementation uses OpenAI instead.

### Permission Issues
We encountered permission issues with log files and directories.

**Solution**: We created the necessary log directories and set appropriate permissions:
sudo mkdir -p /opt/saas-case-analysis/SaasDeployClean/logs
sudo chown -R ec2-user:ec2-user /opt/saas-case-analysis/SaasDeployClean/

## Maintenance Procedures

### Restarting the Application
To restart the application:
sudo systemctl restart saas-application.service

### Checking Application Status
To check if the application is running:
sudo systemctl status saas-application.service
sudo ss -tulpn | grep 5001

### Viewing Application Logs
To view application logs:
sudo journalctl -u saas-application.service -n 50

### Restarting Nginx
To restart Nginx:
sudo systemctl restart nginx

### Checking Nginx Status
To check Nginx status:
sudo systemctl status nginx

### Viewing Nginx Logs
To view Nginx logs:
sudo tail -n 20 /var/log/nginx/error.log
sudo tail -n 20 /var/log/nginx/access.log

## Future Improvements
1. Implement the full functionality of the application using OpenAI instead of Mistral
2. Set up HTTPS with SSL/TLS certificates for secure access
3. Implement proper error handling and logging
4. Add monitoring and alerting for the application
5. Set up automatic backups of the application data

## Contact Information
For any questions or issues regarding this deployment, please contact the deployment team.

## Deployment Date
April 4, 2025
