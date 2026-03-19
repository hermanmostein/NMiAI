# Task 2: Tripletex AI Accounting Agent - Solution Plan

## Competition Overview

**Challenge**: Build an AI agent that completes accounting tasks in Tripletex using natural language prompts in 7 languages.

**Key Requirements**:
- HTTPS endpoint accepting POST requests to `/solve`
- 5-minute timeout per submission
- Handle 30 different task types across 3 difficulty tiers
- Support 7 languages: Norwegian, English, Spanish, Portuguese, Nynorsk, German, French
- Process PDF/image attachments when provided
- Authenticate via Tripletex API proxy
- Return `{"status": "completed"}` when done

**Scoring System**:
- Field-by-field verification (correctness)
- Tier multipliers: Tier 1 (×1), Tier 2 (×2), Tier 3 (×3)
- Efficiency bonus (up to 2× for perfect submissions with minimal API calls and zero errors)
- Maximum score per task: 6.0 (Tier 3 perfect + best efficiency)
- Best score per task is kept (bad runs don't lower score)

## Architecture Design

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Competition Platform                     │
│                  (sends task to /solve)                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Endpoint                          │
│                      (/solve)                                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Request Handler                             │
│  • Parse prompt                                              │
│  • Decode files (base64 → PDF/images)                       │
│  • Extract Tripletex credentials                            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  LLM Task Analyzer                           │
│  • Detect language                                           │
│  • Identify task type (30 types)                            │
│  • Extract entities and parameters                          │
│  • Determine API call sequence                              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Task Executor                               │
│  • Route to appropriate handler                             │
│  • Execute API calls via Tripletex proxy                    │
│  • Handle errors and retries                                │
│  • Track API call efficiency                                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Tripletex API Client                        │
│  • Basic Auth (username: 0, password: session_token)        │
│  • All endpoints via proxy                                  │
│  • Error handling and logging                               │
└─────────────────────────────────────────────────────────────┘
```

### Component Breakdown

#### 1. FastAPI Endpoint (`/solve`)
- **Purpose**: Receive task requests from competition platform
- **Input**: JSON with prompt, files, and Tripletex credentials
- **Output**: `{"status": "completed"}`
- **Timeout**: Must complete within 300 seconds

#### 2. Prompt Parser & Language Detector
- **Purpose**: Understand the task from natural language
- **Languages**: nb, en, es, pt, nn, de, fr
- **Approach**: Use LLM to extract:
  - Task type (create, update, delete, etc.)
  - Entity type (employee, customer, invoice, etc.)
  - Field values (names, emails, dates, amounts)
  - Relationships (customer → invoice, project → customer)

#### 3. File Handler
- **Purpose**: Process PDF and image attachments
- **Capabilities**:
  - Base64 decode
  - PDF text extraction (invoices, contracts, expense reports)
  - OCR for images if needed
  - Extract structured data (amounts, dates, line items)

#### 4. Task Router
- **Purpose**: Map task type to appropriate handler
- **30 Task Types** grouped by category:
  - **Employees**: Create, update, set roles
  - **Customers & Products**: Register, update
  - **Invoicing**: Create invoices, payments, credit notes
  - **Travel Expenses**: Register, delete reports
  - **Projects**: Create, link to customers
  - **Corrections**: Delete, reverse entries
  - **Departments**: Create, enable modules

#### 5. Tripletex API Client
- **Authentication**: Basic Auth with username `0` and session token
- **Key Endpoints**:
  - `/employee` - GET, POST, PUT
  - `/customer` - GET, POST, PUT
  - `/product` - GET, POST
  - `/invoice` - GET, POST
  - `/order` - GET, POST
  - `/travelExpense` - GET, POST, PUT, DELETE
  - `/project` - GET, POST
  - `/department` - GET, POST
  - `/ledger/*` - Various ledger operations

#### 6. Efficiency Optimizer
- **Purpose**: Minimize API calls and errors for higher scores
- **Strategies**:
  - Plan all API calls before execution
  - Avoid unnecessary GET requests
  - Validate data before POST/PUT
  - Parse error messages to fix issues in one retry
  - Cache created entity IDs from responses
  - Use batch operations where available

## Implementation Strategy

### Phase 1: Foundation (Tier 1 Tasks)
**Goal**: Handle simple single-entity operations

**Tasks to Support**:
1. Create employee
2. Create customer
3. Create product
4. Update employee info
5. Update customer info

**Implementation**:
```python
# Example: Create Employee Handler
def handle_create_employee(task_data, api_client):
    # Extract from prompt: name, email, role
    employee_data = {
        "firstName": task_data["first_name"],
        "lastName": task_data["last_name"],
        "email": task_data["email"]
    }
    
    # Single API call
    response = api_client.post("/employee", json=employee_data)
    employee_id = response.json()["value"]["id"]
    
    # If role specified, update permissions
    if task_data.get("role") == "administrator":
        api_client.put(f"/employee/{employee_id}", 
                      json={"isAccountAdministrator": True})
    
    return {"success": True, "employee_id": employee_id}
```

### Phase 2: Multi-Step Workflows (Tier 2 Tasks)
**Goal**: Handle tasks requiring multiple linked API calls

**Tasks to Support**:
1. Create invoice for customer
2. Register payment
3. Issue credit note
4. Create project with customer link
5. Register travel expense

**Implementation Pattern**:
```python
# Example: Create Invoice with Payment
def handle_invoice_with_payment(task_data, api_client):
    # Step 1: Find or create customer
    customer = find_or_create_customer(task_data["customer_name"], api_client)
    
    # Step 2: Create order with line items
    order = api_client.post("/order", json={
        "customer": {"id": customer["id"]},
        "orderLines": task_data["line_items"]
    })
    
    # Step 3: Create invoice from order
    invoice = api_client.post("/invoice", json={
        "invoiceDate": task_data["date"],
        "customer": {"id": customer["id"]},
        "orders": [{"id": order["id"]}]
    })
    
    # Step 4: Register payment if specified
    if task_data.get("payment_amount"):
        api_client.post("/payment", json={
            "invoice": {"id": invoice["id"]},
            "amount": task_data["payment_amount"]
        })
    
    return {"success": True, "invoice_id": invoice["id"]}
```

### Phase 3: Complex Scenarios (Tier 3 Tasks)
**Goal**: Handle advanced workflows with error correction

**Tasks to Support**:
1. Bank reconciliation from CSV
2. Error correction in ledger
3. Year-end closing
4. Complex multi-entity setups

**Key Challenges**:
- File processing (CSV, PDF parsing)
- Multiple entity types
- Validation and error recovery
- Module enablement requirements

### Phase 4: Optimization
**Goal**: Maximize efficiency bonus

**Strategies**:
1. **Pre-flight Planning**: Analyze prompt completely before any API calls
2. **Minimal GET Requests**: Only fetch when necessary, use response IDs
3. **Error Prevention**: Validate all data before POST/PUT
4. **Smart Retries**: Parse error messages, fix in one attempt
5. **Batch Operations**: Use list endpoints where available

**Efficiency Metrics to Track**:
- Total API calls made
- Number of 4xx errors
- Comparison to optimal solution
- Time to completion

## Technology Stack

### Core Framework
- **FastAPI**: Web framework for `/solve` endpoint
- **Uvicorn**: ASGI server
- **Requests**: HTTP client for Tripletex API

### LLM Integration
- **OpenAI GPT-4** or **Anthropic Claude**: For prompt interpretation
- **LangChain**: For structured LLM interactions
- **Pydantic**: For data validation and structured outputs

### File Processing
- **PyPDF2** or **pdfplumber**: PDF text extraction
- **Pillow**: Image processing
- **pytesseract**: OCR if needed

### Utilities
- **python-dotenv**: Environment configuration
- **loguru**: Enhanced logging
- **tenacity**: Retry logic

## Project Structure

```
Task2/
├── main.py                      # FastAPI app entry point
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── config/
│   ├── settings.py             # Configuration management
│   └── task_definitions.py     # Task type definitions
├── api/
│   ├── __init__.py
│   ├── endpoints.py            # /solve endpoint
│   └── models.py               # Request/response models
├── core/
│   ├── __init__.py
│   ├── prompt_parser.py        # LLM-based prompt analysis
│   ├── language_detector.py    # Language identification
│   ├── file_processor.py       # PDF/image handling
│   └── task_router.py          # Route to handlers
├── tripletex/
│   ├── __init__.py
│   ├── client.py               # API client with auth
│   ├── endpoints.py            # Endpoint wrappers
│   └── models.py               # Tripletex data models
├── handlers/
│   ├── __init__.py
│   ├── base.py                 # Base handler class
│   ├── tier1/
│   │   ├── employee.py
│   │   ├── customer.py
│   │   └── product.py
│   ├── tier2/
│   │   ├── invoice.py
│   │   ├── payment.py
│   │   └── project.py
│   └── tier3/
│       ├── reconciliation.py
│       └── corrections.py
├── utils/
│   ├── __init__.py
│   ├── logger.py               # Logging setup
│   ├── efficiency_tracker.py  # API call tracking
│   └── validators.py           # Data validation
└── tests/
    ├── test_handlers.py
    ├── test_api_client.py
    └── test_prompt_parser.py
```

## Development Workflow

### Step 1: Local Development
1. Set up FastAPI endpoint
2. Implement basic Tripletex API client
3. Create simple task handlers (Tier 1)
4. Test with sandbox account

### Step 2: LLM Integration
1. Integrate OpenAI/Claude for prompt parsing
2. Build structured output schemas
3. Test with sample prompts in all 7 languages
4. Refine prompt engineering for accuracy

### Step 3: Handler Implementation
1. Implement all Tier 1 handlers
2. Test each handler individually
3. Implement Tier 2 handlers
4. Implement Tier 3 handlers (as they unlock)

### Step 4: Optimization
1. Add efficiency tracking
2. Minimize API calls
3. Improve error handling
4. Optimize for speed

### Step 5: Deployment
1. Deploy to cloud (Railway, Render, or similar)
2. Ensure HTTPS endpoint
3. Test end-to-end with sandbox
4. Submit to competition platform

## Key Considerations

### Language Support
- All 7 languages must be handled
- LLM should translate/understand all variants
- Test with prompts in each language

### Error Handling
- Every 4xx error reduces efficiency score
- Parse error messages carefully
- Validate before sending requests
- Implement smart retry logic

### API Call Efficiency
- Plan entire workflow before first API call
- Avoid unnecessary GET requests
- Use response data (IDs) instead of re-fetching
- Batch operations where possible

### File Processing
- Some tasks include PDF invoices or expense reports
- Extract structured data accurately
- Handle various PDF formats
- OCR for images if text not embedded

### Timeout Management
- 5-minute hard limit
- Monitor execution time
- Optimize slow operations
- Fail fast if task is impossible

### Testing Strategy
1. **Unit Tests**: Individual handlers
2. **Integration Tests**: Full workflow with sandbox
3. **Language Tests**: Prompts in all 7 languages
4. **Efficiency Tests**: Measure API calls and errors
5. **Edge Cases**: Missing data, invalid inputs, complex scenarios

## Success Metrics

### Correctness
- All required fields created/updated correctly
- Relationships properly linked
- Data validation passes

### Efficiency
- Minimal API calls (compare to optimal)
- Zero 4xx errors (or minimal)
- Fast execution time

### Coverage
- Handle all 30 task types
- Support all 7 languages
- Process all file types

### Score Goals
- **Tier 1**: 1.0+ per task (perfect correctness)
- **Tier 2**: 3.0+ per task (perfect + good efficiency)
- **Tier 3**: 5.0+ per task (perfect + excellent efficiency)

## Next Steps

1. **Set up development environment**
   - Create virtual environment
   - Install dependencies
   - Configure sandbox credentials

2. **Build MVP**
   - FastAPI endpoint
   - Basic Tripletex client
   - One simple handler (create employee)
   - Test with sandbox

3. **Iterate and expand**
   - Add more handlers
   - Improve LLM prompts
   - Optimize efficiency
   - Test thoroughly

4. **Deploy and compete**
   - Deploy to HTTPS endpoint
   - Submit to platform
   - Monitor scores
   - Iterate based on results

## Resources

- **Tripletex API Docs**: https://tripletex.no/execute/docViewer?articleId=853
- **Competition Platform**: https://app.ainm.no/submit/tripletex
- **Sandbox Account**: Available on platform
- **API Proxy**: https://tx-proxy.ainm.no/v2