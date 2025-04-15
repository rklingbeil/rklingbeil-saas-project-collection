# SaaS Case Analysis Application - Access Documentation

## Current Access Methods

### Exposed URL (Recommended)
- **URL**: http://8000-irgkvsfbmg7mlz9eumram-3a4debb8.manus.computer
- **Status**: Working
- **Benefits**:
  - Secure HTTPS connection
  - Stable URL that doesn't change
  - No need to open additional ports on your EC2 instance
  - Works from any network with internet access

### Direct IP Access
- **URL**: http://18.222.244.157:8000
- **Status**: Currently not working due to network configuration changes
- **To restore direct IP access**:
  1. Stop any running Nginx services: `sudo systemctl stop nginx`
  2. Ensure the application is running on port 8000: `cd /home/ubuntu/saas_app && source venv/bin/activate && python app.py`
  3. Configure EC2 security groups to allow inbound traffic on port 8000
  4. Ensure no firewall rules are blocking port 8000

## Starting the Application

To start the FastAPI application manually:

```bash
cd /home/ubuntu/saas_app
source venv/bin/activate
python app.py  # For original FastAPI app
# OR
python enhanced_app.py  # For enhanced FastAPI app with predictive analytics
```

## Permanent Deployment Options

For a truly permanent deployment of your FastAPI application that persists beyond the EC2 instance, consider:

1. **Cloud Platform Services**:
   - AWS Elastic Beanstalk
   - Heroku
   - Google App Engine

2. **Container Deployment**:
   - Dockerize the FastAPI application
   - Deploy to container orchestration services

3. **Serverless Options**:
   - AWS Lambda with API Gateway
   - Google Cloud Functions

## Troubleshooting Access Issues

If you encounter access issues:

1. Check if the application is running:
   ```bash
   ps aux | grep python
   ```

2. Check which ports are in use:
   ```bash
   sudo netstat -tulpn | grep LISTEN
   ```

3. Kill conflicting processes if needed:
   ```bash
   sudo kill -9 [process_id]
   ```

4. Restart the application:
   ```bash
   cd /home/ubuntu/saas_app
   source venv/bin/activate
   python app.py
   ```

5. Expose the port again if needed:
   - Use the deploy_expose_port tool in the sandbox environment
   - Or configure proper port forwarding on your EC2 instance
