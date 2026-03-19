# Railway Deployment - Complete Setup Guide

## ✅ Changes Already Pushed

All necessary files are on GitHub:
- ✅ Dockerfile
- ✅ railway.json
- ✅ Procfile
- ✅ Fixed OPENAI_API_KEY handling
- ✅ Health check endpoint

## 🚀 Railway Setup - Step by Step

### Step 1: Project Settings

In Railway dashboard, configure these settings:

#### A. Root Directory
**CRITICAL**: Set the root directory to `Task2`

1. Go to your Railway project
2. Click on your service
3. Go to "Settings" tab
4. Find "Root Directory"
5. Set it to: `Task2`
6. Click "Save"

**Why**: Your code is in the Task2 subdirectory, not the root.

#### B. Build Settings

Railway should auto-detect from `railway.json`, but verify:

1. Go to "Settings" → "Build"
2. **Builder**: Should be "Dockerfile"
3. **Dockerfile Path**: Should be "Dockerfile"

If not set:
- Builder: Select "Dockerfile"
- Dockerfile Path: `Dockerfile`

#### C. Deploy Settings

1. Go to "Settings" → "Deploy"
2. **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
3. **Health Check Path**: `/health`
4. **Health Check Timeout**: 100 seconds

### Step 2: Environment Variables

Add these in "Variables" tab:

#### Required:
```
OPENAI_API_KEY=sk-your-actual-openai-key-here
```

#### Optional (with defaults):
```
OPENAI_MODEL=gpt-4-turbo-preview
PORT=8000
LOG_LEVEL=INFO
```

**Important**: After adding variables, Railway will automatically redeploy.

### Step 3: Verify Deployment

#### A. Check Build Logs

1. Go to "Deployments" tab
2. Click on the latest deployment
3. Check "Build Logs"

**Should see**:
```
Building with Dockerfile
Step 1/X : FROM python:3.11-slim
...
Successfully built
```

#### B. Check Deploy Logs

Click "Deploy Logs" tab

**Should see**:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

#### C. Test Health Endpoint

Once deployed, get your URL (e.g., `https://your-app.railway.app`)

Test:
```bash
curl https://your-app.railway.app/health
```

**Expected response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "model": "gpt-4-turbo-preview"
}
```

### Step 4: Test the /solve Endpoint

```bash
curl -X POST https://your-app.railway.app/solve \
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

**Expected response**:
```json
{
  "status": "completed"
}
```

## 🐛 Troubleshooting

### Issue 1: "Root Directory Not Set"

**Symptom**: Build fails, can't find files

**Solution**:
1. Settings → Root Directory → Set to `Task2`
2. Redeploy

### Issue 2: "Health Check Failing"

**Symptom**: Deployment fails with "service unavailable"

**Possible Causes**:

#### A. Port Not Binding Correctly
Check deploy logs for:
```
Uvicorn running on http://0.0.0.0:$PORT
```

**Fix**: Ensure start command uses `$PORT`:
```
uvicorn main:app --host 0.0.0.0 --port $PORT
```

#### B. App Crashing on Startup
Check deploy logs for errors.

**Common errors**:
- Missing dependencies: Check requirements.txt
- Import errors: Verify all files are in Task2/
- Configuration errors: Check environment variables

#### C. Health Check Path Wrong
**Fix**: Set health check path to `/health` (not `/healthcheck`)

### Issue 3: "OPENAI_API_KEY Not Working"

**Symptom**: Health check passes but /solve fails

**Check**:
1. Variable is named exactly: `OPENAI_API_KEY`
2. Value starts with `sk-`
3. No extra spaces or quotes
4. Railway redeployed after adding variable

**Test**:
```bash
# Should work
curl https://your-app.railway.app/health

# Should return error if key is wrong
curl -X POST https://your-app.railway.app/solve \
  -H "Content-Type: application/json" \
  -d '{"prompt":"test","files":[],"tripletex_credentials":{"base_url":"https://test","session_token":"test"}}'
```

### Issue 4: "Build Succeeds but Deploy Fails"

**Check Deploy Logs** for:

#### A. Missing System Dependencies
If you see errors about missing libraries, update Dockerfile:
```dockerfile
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*
```

#### B. Python Version Issues
Ensure Dockerfile uses Python 3.11:
```dockerfile
FROM python:3.11-slim
```

#### C. Port Already in Use
Railway assigns a random port via $PORT variable.
Ensure your start command uses it:
```
uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Issue 5: "Dockerfile Not Found"

**Symptom**: "Could not find Dockerfile"

**Solution**:
1. Verify Root Directory is set to `Task2`
2. Verify Dockerfile exists in Task2/
3. Check Dockerfile path in settings: should be just `Dockerfile`

## 📋 Railway Configuration Checklist

- [ ] Root Directory set to `Task2`
- [ ] Builder set to "Dockerfile"
- [ ] Dockerfile path set to `Dockerfile`
- [ ] Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- [ ] Health check path: `/health`
- [ ] Health check timeout: 100 seconds
- [ ] Environment variable `OPENAI_API_KEY` added
- [ ] Latest code pulled from GitHub
- [ ] Build logs show success
- [ ] Deploy logs show "Uvicorn running"
- [ ] Health endpoint returns 200 OK
- [ ] /solve endpoint works with test request

## 🎯 Alternative: Use Render Instead

If Railway continues to have issues, Render is simpler for Python apps:

### Render Setup (5 minutes):

1. Go to https://render.com
2. Click "New +" → "Web Service"
3. Connect GitHub: `hermanmostein/NMiAI`
4. Settings:
   - **Name**: `tripletex-agent`
   - **Root Directory**: `Task2`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Environment Variables:
   - Add: `OPENAI_API_KEY` = `sk-your-key`
6. Click "Create Web Service"

Render will:
- ✅ Auto-detect Python
- ✅ Install dependencies
- ✅ Start the app
- ✅ Provide HTTPS URL
- ✅ Free tier available

## 🔍 Debugging Commands

### Check if app is running:
```bash
curl https://your-app.railway.app/
```

### Check health:
```bash
curl https://your-app.railway.app/health
```

### Test with verbose output:
```bash
curl -v https://your-app.railway.app/health
```

### Check Railway logs:
1. Go to Railway dashboard
2. Click your service
3. Click "Deployments"
4. Click latest deployment
5. View "Build Logs" and "Deploy Logs"

## ✅ Success Indicators

When everything works, you should see:

1. **Build Logs**: "Successfully built"
2. **Deploy Logs**: "Uvicorn running on http://0.0.0.0:$PORT"
3. **Health Check**: Returns `{"status": "healthy"}`
4. **Railway Status**: Green checkmark
5. **URL**: Accessible via HTTPS

## 🎉 Once Working

1. Get your Railway URL
2. Test /solve endpoint with sandbox credentials
3. Submit URL to competition: https://app.ainm.no/submit/tripletex
4. Monitor your scores!

## 💡 Pro Tips

1. **Check logs first**: Most issues are visible in deploy logs
2. **Test health endpoint**: Should work before testing /solve
3. **Verify environment variables**: No spaces, correct names
4. **Use Render if stuck**: It's more Python-friendly
5. **Root directory is critical**: Must be set to `Task2`

## 📞 Still Having Issues?

Share these details:
1. Railway build logs (last 20 lines)
2. Railway deploy logs (last 20 lines)
3. Error message from health check
4. Your Railway settings (root directory, start command)
5. Environment variables (names only, not values)