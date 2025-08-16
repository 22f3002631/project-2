# Deployment Guide

This guide explains how to deploy the Data Analyst Agent to various platforms.

## Prerequisites

- Python 3.11+
- Git
- Account on deployment platform (Heroku, Railway, Render, etc.)

## Platform-Specific Deployment

### Heroku

1. **Install Heroku CLI**
   ```bash
   # Download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Login to Heroku**
   ```bash
   heroku login
   ```

3. **Create Heroku App**
   ```bash
   heroku create your-unique-app-name
   ```

4. **Deploy**
   ```bash
   git add .
   git commit -m "Initial deployment"
   git push heroku main
   ```

5. **Set Environment Variables (Optional)**
   ```bash
   heroku config:set OPENAI_API_KEY=your_openai_key
   heroku config:set ANTHROPIC_API_KEY=your_anthropic_key
   ```

6. **Open App**
   ```bash
   heroku open
   ```

### Railway

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login and Deploy**
   ```bash
   railway login
   railway init
   railway up
   ```

### Render

1. **Connect GitHub Repository**
   - Go to https://render.com
   - Connect your GitHub repository
   - Choose "Web Service"

2. **Configure Build Settings**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Python Version: 3.11.5

### Google Cloud Run

1. **Build Docker Image**
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/data-analyst-agent
   ```

2. **Deploy to Cloud Run**
   ```bash
   gcloud run deploy --image gcr.io/PROJECT_ID/data-analyst-agent --platform managed
   ```

## Environment Variables

The application supports these optional environment variables:

- `OPENAI_API_KEY`: OpenAI API key for enhanced LLM capabilities
- `ANTHROPIC_API_KEY`: Anthropic API key for Claude integration
- `PORT`: Port number (automatically set by most platforms)

## Testing Deployment

After deployment, test your API:

```bash
# Health check
curl https://your-app-url.com/health

# Test with sample question
curl -X POST https://your-app-url.com/api/ \
  -F "questions.txt=@sample_questions/wikipedia_example.txt"
```

## Troubleshooting

### Common Issues

1. **Build Timeout**
   - Increase build timeout in platform settings
   - Optimize requirements.txt (remove unused packages)

2. **Memory Issues**
   - Upgrade to higher memory tier
   - Optimize data processing (process in chunks)

3. **Request Timeout**
   - Increase request timeout settings
   - Implement request queuing for long-running tasks

### Logs

Check application logs:

```bash
# Heroku
heroku logs --tail

# Railway
railway logs

# Render
# Check logs in dashboard
```

## Performance Optimization

1. **Caching**
   - Implement Redis for caching scraped data
   - Cache visualization results

2. **Async Processing**
   - Use Celery for background tasks
   - Implement request queuing

3. **Database**
   - Add PostgreSQL for persistent storage
   - Store analysis results

## Security

1. **API Keys**
   - Store in environment variables
   - Use platform secret management

2. **Rate Limiting**
   - Implement Flask-Limiter
   - Add request validation

3. **CORS**
   - Configure appropriate CORS settings
   - Restrict origins in production
