# Task 2: Quick Start Guide

## Prerequisites

- Python 3.9+
- pip or poetry for package management
- Access to Tripletex sandbox account
- OpenAI API key or Anthropic API key (for LLM)
- HTTPS endpoint for deployment (Railway, Render, or similar)

## Step 1: Set Up Development Environment

```bash
# Navigate to Task2 directory
cd Task2

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure Environment Variables

Create a `.env` file in the Task2 directory:

```env
# LLM Configuration
OPENAI_API_KEY=your_openai_api_key_here
# OR
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Tripletex Sandbox (for local testing)
SANDBOX_BASE_URL=https://kkpqfuj-amager.tripletex.dev/v2
SANDBOX_SESSION_TOKEN=your_sandbox_token_here

# Server Configuration
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO

# Optional: API Key for endpoint protection
API_KEY=your_secret_api_key_here
```

## Step 3: Run Locally

```bash
# Start the FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Server will be available at http://localhost:8000
```

## Step 4: Test with Sandbox

### Option A: Using curl

```bash
curl -X POST http://localhost:8000/solve \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Opprett en ansatt med navn Ola Nordmann, ola@example.org",
    "files": [],
    "tripletex_credentials": {
      "base_url": "https://kkpqfuj-amager.tripletex.dev/v2",
      "session_token": "your_sandbox_token"
    }
  }'
```

### Option B: Using Python

```python
import requests

response = requests.post(
    "http://localhost:8000/solve",
    json={
        "prompt": "Opprett en ansatt med navn Ola Nordmann, ola@example.org",
        "files": [],
        "tripletex_credentials": {
            "base_url": "https://kkpqfuj-amager.tripletex.dev/v2",
            "session_token": "your_sandbox_token"
        }
    }
)

print(response.json())
```

### Option C: Using the test script

```bash
python test_local.py
```

## Step 5: Expose Locally via HTTPS (for testing)

```bash
# Install cloudflared
# On macOS:
brew install cloudflare/cloudflare/cloudflared

# Create tunnel
cloudflared tunnel --url http://localhost:8000

# You'll get a URL like: https://random-name.trycloudflare.com
# Use this URL for testing with the competition platform
```

## Step 6: Deploy to Production

### Option A: Railway

1. Create account at https://railway.app
2. Create new project
3. Connect GitHub repository
4. Set environment variables in Railway dashboard
5. Deploy
6. Get HTTPS URL

### Option B: Render

1. Create account at https://render.com
2. Create new Web Service
3. Connect GitHub repository
4. Set environment variables
5. Deploy
6. Get HTTPS URL

### Option C: Google Cloud Run

```bash
# Build container
docker build -t tripletex-agent .

# Tag for GCR
docker tag tripletex-agent gcr.io/YOUR_PROJECT/tripletex-agent

# Push to GCR
docker push gcr.io/YOUR_PROJECT/tripletex-agent

# Deploy to Cloud Run
gcloud run deploy tripletex-agent \
  --image gcr.io/YOUR_PROJECT/tripletex-agent \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Step 7: Submit to Competition

1. Go to https://app.ainm.no/submit/tripletex
2. Enter your HTTPS endpoint URL
3. Optionally set an API key for protection
4. Click "Submit"
5. Monitor your submissions and scores

## Development Workflow

### 1. Test Individual Handlers

```python
# test_handlers.py
from handlers.tier1.employee import EmployeeHandler
from tripletex.client import TripletexClient

# Initialize client with sandbox credentials
client = TripletexClient(
    base_url="https://kkpqfuj-amager.tripletex.dev/v2",
    session_token="your_token"
)

# Test employee handler
handler = EmployeeHandler(client, None)
result = handler.execute({
    "task_type": "create_employee",
    "entities": {
        "employee": {
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com"
        }
    },
    "special_instructions": {}
})

print(result)
```

### 2. Test LLM Prompt Parsing

```python
# test_llm.py
from core.prompt_parser import analyze_prompt

prompt = "Opprett en ansatt med navn Ola Nordmann, ola@example.org"
result = analyze_prompt(prompt)
print(result)
```

### 3. Monitor Logs

```bash
# Tail logs in real-time
tail -f logs/tripletex_agent.log

# Or use the logging dashboard if deployed
```

### 4. Check API Efficiency

```python
# After each task, check efficiency stats
stats = api_client.get_efficiency_stats()
print(f"Total calls: {stats['total_calls']}")
print(f"Errors: {stats['error_calls']}")
print(f"Success rate: {stats['success_rate']:.2%}")
```

## Troubleshooting

### Issue: 401 Unauthorized

**Cause**: Wrong authentication format

**Solution**: Ensure you're using Basic Auth with username `0` and session token as password

```python
auth = ("0", session_token)  # Correct
# NOT: auth = (session_token, "")
```

### Issue: 422 Validation Error

**Cause**: Missing required fields

**Solution**: Check the error message for which fields are required

```python
try:
    response = api.post("/employee", json=data)
except requests.exceptions.HTTPError as e:
    error_data = e.response.json()
    print(f"Validation error: {error_data['message']}")
    # Fix the missing fields and retry
```

### Issue: Timeout (5 minutes)

**Cause**: Agent taking too long

**Solution**: Optimize API calls, reduce unnecessary requests

```python
# Bad: Multiple GET requests
customer = api.get("/customer", params={"name": "Acme"})
product = api.get("/product", params={"name": "Widget"})

# Good: Use response IDs, avoid redundant GETs
customer_id = create_customer_response["value"]["id"]
```

### Issue: Empty values array

**Cause**: No results found in search

**Solution**: Create the entity if it doesn't exist

```python
response = api.get("/customer", params={"name": "Acme"})
customers = response.json().get("values", [])

if not customers:
    # Create new customer
    response = api.post("/customer", json={"name": "Acme", "isCustomer": True})
    customer = response.json()["value"]
else:
    customer = customers[0]
```

## Testing Checklist

Before submitting to competition:

- [ ] Test with Norwegian prompts
- [ ] Test with English prompts
- [ ] Test with other languages (es, pt, nn, de, fr)
- [ ] Test with file attachments (PDF, images)
- [ ] Test all Tier 1 tasks
- [ ] Test all Tier 2 tasks (when unlocked)
- [ ] Test all Tier 3 tasks (when unlocked)
- [ ] Verify HTTPS endpoint is accessible
- [ ] Check logs for errors
- [ ] Verify efficiency (minimal API calls)
- [ ] Test timeout handling (< 5 minutes)
- [ ] Test error recovery
- [ ] Verify response format: `{"status": "completed"}`

## Performance Optimization Tips

1. **Plan before executing**: Analyze the entire prompt before making any API calls
2. **Avoid trial-and-error**: Validate data before sending to avoid 4xx errors
3. **Cache responses**: Don't re-fetch entities you just created
4. **Batch operations**: Use list endpoints when possible
5. **Parse error messages**: Fix issues in one retry, not multiple
6. **Use specific fields**: `?fields=id,name` instead of fetching all fields
7. **Minimize GET calls**: Only fetch when absolutely necessary

## Monitoring Your Score

1. Go to https://app.ainm.no/submit/tripletex
2. View your submission history
3. Check scores per task type
4. Review API call logs for each submission
5. Identify areas for improvement
6. Iterate and resubmit

## Next Steps

1. **Start with Tier 1**: Build handlers for simple tasks first
2. **Test thoroughly**: Use sandbox to verify each handler works
3. **Add Tier 2**: Implement multi-step workflows
4. **Optimize**: Reduce API calls and errors
5. **Add Tier 3**: Tackle complex scenarios when unlocked
6. **Compete**: Submit regularly and track your progress

## Resources

- **Competition Rules**: [`Competition_rules.md`](./Competition_rules.md)
- **Solution Plan**: [`SOLUTION_PLAN.md`](./SOLUTION_PLAN.md)
- **Implementation Guide**: [`IMPLEMENTATION_GUIDE.md`](./IMPLEMENTATION_GUIDE.md)
- **Tripletex API Docs**: https://tripletex.no/execute/docViewer?articleId=853
- **Competition Platform**: https://app.ainm.no/submit/tripletex