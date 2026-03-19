# Task 2: Tripletex AI Accounting Agent

## Overview

This is an AI agent that completes accounting tasks in Tripletex using natural language prompts. The agent receives task descriptions in one of 7 languages, interprets them using an LLM, executes the appropriate Tripletex API calls, and gets scored on correctness and efficiency.

## Competition Details

- **Platform**: https://app.ainm.no/submit/tripletex
- **Task Types**: 30 different accounting operations
- **Languages**: Norwegian, English, Spanish, Portuguese, Nynorsk, German, French
- **Timeout**: 5 minutes per submission
- **Scoring**: Field-by-field verification + efficiency bonus
- **Max Score**: 6.0 per task (Tier 3 perfect + best efficiency)

## Key Features

- ✅ FastAPI endpoint accepting POST requests to `/solve`
- ✅ LLM-powered prompt interpretation (OpenAI/Anthropic)
- ✅ Multi-language support (7 languages)
- ✅ PDF and image file processing
- ✅ Tripletex API client with authentication
- ✅ Task routing to specialized handlers
- ✅ Efficiency tracking and optimization
- ✅ Comprehensive error handling
- ✅ Logging and monitoring

## Architecture

```
Competition Platform → FastAPI Endpoint → LLM Analyzer → Task Router → Handlers → Tripletex API
```

### Components

1. **FastAPI Endpoint** (`/solve`) - Receives task requests
2. **Prompt Parser** - LLM-based natural language understanding
3. **File Processor** - Handles PDF/image attachments
4. **Task Router** - Routes to appropriate handler
5. **Handlers** - Execute specific task types (30 types across 3 tiers)
6. **Tripletex Client** - API communication with authentication
7. **Efficiency Tracker** - Monitors API calls and errors

## Task Tiers

### Tier 1 (×1 multiplier)
- Create/update employees
- Create/update customers
- Create/update products

### Tier 2 (×2 multiplier)
- Create invoices with payments
- Register travel expenses
- Create projects
- Issue credit notes

### Tier 3 (×3 multiplier)
- Bank reconciliation from CSV
- Error correction in ledger
- Year-end closing
- Complex multi-entity workflows

## Quick Start

### 1. Prerequisites
```bash
# Python 3.9+
python --version

# Get Tripletex sandbox account from platform
# Get OpenAI or Anthropic API key
```

### 2. Setup
```bash
cd Task2
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
```

### 3. Run Locally
```bash
uvicorn main:app --reload
```

### 4. Test
```bash
curl -X POST http://localhost:8000/solve \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Opprett en ansatt med navn Ola Nordmann, ola@example.org",
    "files": [],
    "tripletex_credentials": {
      "base_url": "https://kkpqfuj-amager.tripletex.dev/v2",
      "session_token": "your_token"
    }
  }'
```

### 5. Deploy
```bash
# Railway, Render, or Google Cloud Run
# See QUICK_START.md for detailed deployment instructions
```

### 6. Submit
1. Go to https://app.ainm.no/submit/tripletex
2. Enter your HTTPS endpoint URL
3. Submit and monitor scores

## Documentation

- **[Competition Rules](./Competition_rules.md)** - Full competition specifications
- **[Solution Plan](./SOLUTION_PLAN.md)** - Comprehensive architecture and strategy
- **[Implementation Guide](./IMPLEMENTATION_GUIDE.md)** - Code patterns and examples
- **[Project Setup](./PROJECT_SETUP.md)** - Project structure and configuration
- **[Quick Start](./QUICK_START.md)** - Step-by-step getting started guide

## Project Structure

```
Task2/
├── main.py                      # FastAPI application
├── requirements.txt             # Dependencies
├── .env                        # Configuration (gitignored)
├── config/                     # Settings and task definitions
├── api/                        # Endpoint implementations
├── core/                       # Prompt parsing, routing
├── tripletex/                  # API client
├── handlers/                   # Task handlers (tier1, tier2, tier3)
├── utils/                      # Logging, tracking, validation
└── tests/                      # Unit and integration tests
```

## Development Workflow

1. **Implement handlers** - Start with Tier 1 tasks
2. **Test with sandbox** - Verify each handler works
3. **Optimize efficiency** - Minimize API calls and errors
4. **Add more tiers** - Expand to Tier 2 and 3
5. **Deploy and compete** - Submit and iterate

## Scoring Strategy

### Correctness (Base Score)
- Field-by-field verification
- All required fields must match expected values
- Relationships properly linked

### Tier Multiplier
- Tier 1: ×1
- Tier 2: ×2
- Tier 3: ×3

### Efficiency Bonus (up to 2×)
- Minimal API calls (compared to optimal solution)
- Zero or minimal 4xx errors
- Fast execution time

**Example**: Perfect Tier 2 task with excellent efficiency = 1.0 × 2 × 2 = 4.0 points

## Optimization Tips

1. **Plan before executing** - Analyze entire prompt first
2. **Avoid trial-and-error** - Validate data before API calls
3. **Cache responses** - Use IDs from responses, don't re-fetch
4. **Parse error messages** - Fix issues in one retry
5. **Minimize GET calls** - Only fetch when necessary
6. **Use specific fields** - `?fields=id,name` instead of all fields

## Common Patterns

### Create Employee
```
Prompt → Extract name/email → POST /employee → Set role if needed
```

### Create Invoice
```
Prompt → Find/create customer → Find/create products → 
POST /order → POST /invoice → Register payment if specified
```

### Multi-step Workflow
```
Prompt → Identify dependencies → Create in correct order → 
Link entities → Verify completion
```

## Testing

```bash
# Unit tests
pytest tests/test_handlers.py

# Integration tests with sandbox
pytest tests/test_integration.py

# Test specific language
python scripts/test_language.py --lang nb

# Test efficiency
python scripts/test_efficiency.py
```

## Monitoring

- **Logs**: `logs/tripletex_agent.log`
- **Metrics**: API calls, errors, execution time
- **Platform**: View submission history and scores
- **Debugging**: API call logs available per submission

## Resources

- **Tripletex API Docs**: https://tripletex.no/execute/docViewer?articleId=853
- **Competition Platform**: https://app.ainm.no/submit/tripletex
- **Sandbox Account**: Available on platform
- **Support**: Check platform documentation and forums

## Status

📋 **Planning Phase Complete**

Next steps:
1. Set up development environment
2. Implement core components
3. Build Tier 1 handlers
4. Test with sandbox
5. Deploy and compete

## License

Competition project for Norwegian AI Competition 2026

---

**Ready to build?** See [`QUICK_START.md`](./QUICK_START.md) to begin implementation.