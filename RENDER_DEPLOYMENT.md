# Render Cloud Platform Deployment Guide

This guide provides step-by-step instructions for deploying the Data Analyst Agent to Render Cloud Platform.

## Prerequisites

- GitHub account with your project repository
- Render account (free tier available at https://render.com)
- Project code pushed to a public GitHub repository

## Step 1: Prepare Your Repository

Ensure your GitHub repository contains all required files:

```
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── data_sourcing.py         # Data sourcing module
├── data_analysis.py         # Analysis module
├── data_visualization.py    # Visualization module
├── question_processor.py    # Question processing
├── llm_integration.py       # LLM integration
├── LICENSE                  # MIT License (required)
├── README.md               # Project documentation
└── sample_questions/       # Example questions
```

## Step 2: Create Render Account

1. Go to https://render.com
2. Click "Get Started for Free"
3. Sign up using your GitHub account
4. Authorize Render to access your repositories

## Step 3: Create New Web Service

1. **Dashboard Access**
   - Log into your Render dashboard
   - Click "New +" button in the top right
   - Select "Web Service"

2. **Connect Repository**
   - Choose "Build and deploy from a Git repository"
   - Click "Connect" next to your GitHub account
   - Select your data-analyst-agent repository
   - Click "Connect"

## Step 4: Configure Build Settings

### Basic Configuration
- **Name**: `data-analyst-agent` (or your preferred name)
- **Region**: Choose closest to your location
- **Branch**: `main` (or your default branch)
- **Root Directory**: Leave blank (unless code is in subdirectory)

### Build Configuration
- **Runtime**: `Python 3`
- **Build Command**: 
  ```bash
  pip install -r requirements.txt
  ```
- **Start Command**:
  ```bash
  gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 300
  ```

### Advanced Settings
- **Python Version**: `3.11.5` (add in Environment Variables)
- **Auto-Deploy**: `Yes` (recommended)

## Step 5: Environment Variables

Add the following environment variables in the Render dashboard:

### Required Variables
```
PYTHON_VERSION=3.11.5
PORT=10000
```

### Optional Variables (for enhanced functionality)
```
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

**To add environment variables:**
1. In your service settings, scroll to "Environment Variables"
2. Click "Add Environment Variable"
3. Enter key-value pairs as shown above
4. Click "Save Changes"

## Step 6: Deploy Application

1. **Initial Deployment**
   - Click "Create Web Service"
   - Render will automatically start building your application
   - Build process typically takes 2-5 minutes

2. **Monitor Build Process**
   - Watch the build logs in real-time
   - Look for successful installation of dependencies
   - Ensure no critical errors occur

3. **Deployment Completion**
   - Service will show "Live" status when ready
   - You'll receive a URL like: `https://your-app-name.onrender.com`

## Step 7: Test Deployed Application

### Health Check
```bash
curl https://your-app-name.onrender.com/health
```

Expected response:
```json
{"status":"healthy","timestamp":"2025-08-16T10:30:00.000000"}
```

### API Test with Sample Question
```bash
curl -X POST https://project-2-nn6u.onrender.com/api/ \
  -F "questions.txt=@sample_questions/wikipedia_example.txt"
```

### Test with Simple Question
Create a test file `test_question.txt`:
```
What is 2 + 2?
```

Then test:
```bash
curl -X POST https://your-app-name.onrender.com/api/ \
  -F "questions.txt=@test_question.txt"
```

## Step 8: Configure Custom Domain (Optional)

1. **Add Custom Domain**
   - Go to service settings
   - Click "Custom Domains"
   - Add your domain name
   - Follow DNS configuration instructions

2. **SSL Certificate**
   - Render automatically provides SSL certificates
   - No additional configuration needed

## Troubleshooting

### Common Build Issues

1. **Dependency Installation Failures**
   ```
   Solution: Check requirements.txt for version conflicts
   Update to compatible versions if needed
   ```

2. **Memory Limit Exceeded**
   ```
   Solution: Upgrade to paid plan for more memory
   Or optimize code to use less memory
   ```

3. **Build Timeout**
   ```
   Solution: Optimize requirements.txt
   Remove unnecessary dependencies
   ```

### Runtime Issues

1. **Application Won't Start**
   - Check start command syntax
   - Verify app.py contains Flask app instance
   - Review application logs

2. **Import Errors**
   - Ensure all Python files are in repository
   - Check for missing dependencies in requirements.txt

3. **API Timeouts**
   - Verify timeout settings in gunicorn command
   - Check application timeout handling

### Monitoring and Logs

1. **Access Logs**
   - Go to your service dashboard
   - Click "Logs" tab
   - Monitor real-time application logs

2. **Performance Metrics**
   - View CPU and memory usage
   - Monitor response times
   - Check error rates

## Render-Specific Optimizations

### Performance Settings
```bash
# Optimized start command for Render
gunicorn app:app \
  --bind 0.0.0.0:$PORT \
  --workers 1 \
  --timeout 300 \
  --max-requests 100 \
  --max-requests-jitter 10 \
  --preload
```

### Health Check Configuration
Render automatically monitors your `/health` endpoint for service health.

### Scaling Options
- **Free Tier**: 1 instance, 512MB RAM
- **Paid Plans**: Multiple instances, more RAM
- **Auto-scaling**: Available on higher tiers

## Security Best Practices

1. **Environment Variables**
   - Never commit API keys to repository
   - Use Render's environment variable system
   - Rotate keys regularly

2. **HTTPS**
   - Always use HTTPS URLs
   - Render provides automatic SSL

3. **Access Control**
   - Consider adding API authentication
   - Implement rate limiting for production

## Cost Optimization

1. **Free Tier Limits**
   - 750 hours per month
   - Service sleeps after 15 minutes of inactivity
   - Cold start delay when waking up

2. **Paid Plans**
   - Always-on services
   - Faster performance
   - More resources

## Support and Resources

- **Render Documentation**: https://render.com/docs
- **Community Forum**: https://community.render.com
- **Status Page**: https://status.render.com
- **Support**: Available through dashboard

## Final Verification

After deployment, verify your API meets the testing requirements:

1. **Concurrent Request Handling**: Test multiple simultaneous requests
2. **Timeout Compliance**: Ensure responses within 5-minute limit
3. **JSON Format**: Verify all responses are valid JSON
4. **Error Handling**: Test with invalid inputs

Your Data Analyst Agent is now successfully deployed on Render and ready for automated testing!
