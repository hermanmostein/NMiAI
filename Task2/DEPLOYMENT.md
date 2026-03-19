# Deployment Guide

## Quick Deploy to Railway (Recommended)

Railway offers one-click deployment with automatic HTTPS.

### Step 1: Prepare Repository

```bash
cd Task2
git init
git add .
git commit -m "Initial commit: Tripletex AI Agent"
```

### Step 2: Push to GitHub

```bash
# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/tripletex-agent.git
git branch -M main
git push -u origin main
```

### Step 3: Deploy to Railway

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Railway will auto-detect the Dockerfile

### Step 4: Configure Environment Variables

In Railway dashboard, add these variables:

```
OPENAI_API_KEY=sk-your-openai-key-here
OPENAI_MODEL=gpt-4-turbo-preview
PORT=8000
```

Optional:
```
API_KEY=your-secret-key-for-endpoint-protection
LOG_LEVEL=INFO
```

### Step 5: Get Your URL

Railway will provide a URL like: `https://your-app.railway.app`

### Step 6: Test

```bash
curl https://your-app.railway.app/health
```

### Step 7: Submit to Competition

Go to https://app.ainm.no/submit/tripletex and enter your Railway URL.

---

## Alternative: Deploy to Render

### Step 1: Create Render Account

Go to https://render.com and sign up.

### Step 2: Create New Web Service

1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: tripletex-agent
   - **Environment**: Docker
   - **Region**: Choose closest to you
   - **Instance Type**: Free or Starter

### Step 3: Environment Variables

Add in Render dashboard:

```
OPENAI_API_KEY=sk-your-openai-key-here
OPENAI_MODEL=gpt-4-turbo-preview
PORT=8000
```

### Step 4: Deploy

Click "Create Web Service" - Render will build and deploy automatically.

### Step 5: Get URL

Render provides: `https://tripletex-agent.onrender.com`

---

## Alternative: Deploy to Google Cloud Run

### Prerequisites

```bash
# Install Google Cloud SDK
# macOS:
brew install google-cloud-sdk

# Initialize
gcloud init
gcloud auth login
```

### Step 1: Build and Push Container

```bash
cd Task2

# Set project ID
export PROJECT_ID=your-gcp-project-id
export REGION=us-central1

# Build container
gcloud builds submit --tag gcr.io/$PROJECT_ID/tripletex-agent

# Or build locally and push
docker build -t gcr.io/$PROJECT_ID/tripletex-agent .
docker push gcr.io/$PROJECT_ID/tripletex-agent
```

### Step 2: Deploy to Cloud Run

```bash
gcloud run deploy tripletex-agent \
  --image gcr.io/$PROJECT_ID/tripletex-agent \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=sk-your-key-here,OPENAI_MODEL=gpt-4-turbo-preview \
  --memory 1Gi \
  --timeout 300s
```

### Step 3: Get URL

Cloud Run will output the service URL.

---

## Local Development with HTTPS (for testing)

### Option 1: Cloudflare Tunnel

```bash
# Install cloudflared
brew install cloudflare/cloudflare/cloudflared

# Start your app
cd Task2
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

# In another terminal, create tunnel
cloudflared tunnel --url http://localhost:8000
```

You'll get a URL like: `https://random-name.trycloudflare.com`

### Option 2: ngrok

```bash
# Install ngrok
brew install ngrok

# Start your app
uvicorn main:app --reload

# In another terminal
ngrok http 8000
```

---

## Environment Variables Reference

### Required

- `OPENAI_API_KEY` - Your OpenAI API key (starts with sk-)

### Optional

- `OPENAI_MODEL` - Model to use (default: gpt-4-turbo-preview)
- `API_KEY` - Secret key to protect your endpoint
- `HOST` - Host to bind to (default: 0.0.0.0)
- `PORT` - Port to listen on (default: 8000)
- `LOG_LEVEL` - Logging level (default: INFO)

---

## Testing Your Deployment

### Health Check

```bash
curl https://your-app-url.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "model": "gpt-4-turbo-preview"
}
```

### Test with Sample Task

```bash
curl -X POST https://your-app-url.com/solve \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create an employee named John Doe with email john@example.com",
    "files": [],
    "tripletex_credentials": {
      "base_url": "https://your-sandbox.tripletex.dev/v2",
      "session_token": "your-sandbox-token"
    }
  }'
```

Expected response:
```json
{
  "status": "completed"
}
```

---

## Monitoring

### View Logs

**Railway:**
- Go to your project → Deployments → View Logs

**Render:**
- Go to your service → Logs tab

**Google Cloud Run:**
```bash
gcloud run services logs read tripletex-agent --region $REGION
```

### Check Performance

Monitor these metrics:
- Response time (should be < 30 seconds for most tasks)
- Error rate (should be < 5%)
- API call efficiency (fewer calls = better score)

---

## Troubleshooting

### Issue: 500 Internal Server Error

**Check logs for:**
- Missing OPENAI_API_KEY
- Invalid API key
- OpenAI API rate limits

**Solution:**
```bash
# Verify environment variable is set
echo $OPENAI_API_KEY

# Check OpenAI API status
curl https://status.openai.com/
```

### Issue: Timeout (5 minutes)

**Causes:**
- LLM taking too long
- Too many API calls
- Network issues

**Solutions:**
- Use faster model (gpt-3.5-turbo)
- Optimize API call sequence
- Add timeout handling

### Issue: 401 Unauthorized from Tripletex

**Causes:**
- Wrong session token
- Expired token
- Incorrect auth format

**Solution:**
- Verify token in sandbox
- Check auth is ("0", token)

### Issue: High Error Rate

**Check:**
- API call validation
- Error handling logic
- Retry mechanism

---

## Scaling Considerations

### For High Volume

1. **Use faster model**: gpt-3.5-turbo instead of gpt-4
2. **Add caching**: Cache common task patterns
3. **Parallel processing**: Handle multiple tasks concurrently
4. **Database**: Store task history and learnings

### Cost Optimization

1. **Monitor OpenAI usage**: Track token consumption
2. **Optimize prompts**: Shorter prompts = lower cost
3. **Cache results**: Avoid redundant LLM calls
4. **Use cheaper models**: For simple tasks

---

## Security Best Practices

1. **Set API_KEY**: Protect your endpoint
2. **Rotate keys**: Change API keys regularly
3. **Monitor usage**: Watch for unusual activity
4. **Rate limiting**: Add rate limits if needed
5. **HTTPS only**: Never use HTTP in production

---

## Competition Submission

### Final Checklist

- [ ] Deployment is live and accessible
- [ ] Health check returns 200 OK
- [ ] Test task completes successfully
- [ ] Logs show no errors
- [ ] HTTPS URL (not HTTP)
- [ ] Environment variables configured
- [ ] API key set (if using endpoint protection)

### Submit

1. Go to https://app.ainm.no/submit/tripletex
2. Enter your HTTPS URL
3. Optionally set API key
4. Click "Submit"
5. Monitor your submissions and scores

### After Submission

- Watch the leaderboard
- Review API call logs for each submission
- Identify areas for improvement
- Iterate and resubmit

---

## Support

- **Competition Platform**: https://app.ainm.no
- **Tripletex API Docs**: https://tripletex.no/execute/docViewer?articleId=853
- **OpenAI Docs**: https://platform.openai.com/docs