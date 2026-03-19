# Task 2: Implementation Guide

## LLM Prompt Engineering

### System Prompt for Task Analysis

```python
TASK_ANALYSIS_PROMPT = """You are an expert at analyzing accounting task prompts for the Tripletex API.

Given a prompt in any of these languages (Norwegian, English, Spanish, Portuguese, Nynorsk, German, French), 
extract the following information in a structured format:

1. **Task Type**: One of:
   - create_employee, update_employee, delete_employee
   - create_customer, update_customer, delete_customer
   - create_product, update_product
   - create_invoice, create_payment, create_credit_note
   - create_travel_expense, delete_travel_expense
   - create_project, update_project
   - create_department, enable_module
   - delete_voucher, reverse_posting
   - bank_reconciliation, year_end_closing

2. **Entities**: Extract all entity details mentioned:
   - Names (first, last, company)
   - Email addresses
   - Phone numbers
   - Addresses
   - Amounts and currencies
   - Dates
   - Roles/permissions
   - Product details
   - Invoice line items

3. **Relationships**: Identify connections:
   - Customer → Invoice
   - Project → Customer
   - Employee → Department
   - Order → Invoice

4. **Special Instructions**: Any specific requirements:
   - Administrator role
   - Specific account numbers
   - Payment terms
   - Due dates

Return your analysis as JSON with this structure:
{
  "task_type": "create_employee",
  "language": "nb",
  "entities": {
    "employee": {
      "first_name": "Ola",
      "last_name": "Nordmann",
      "email": "ola@example.org"
    }
  },
  "special_instructions": {
    "role": "administrator"
  },
  "api_sequence": [
    {"endpoint": "/employee", "method": "POST", "purpose": "Create employee"},
    {"endpoint": "/employee/{id}", "method": "PUT", "purpose": "Set administrator role"}
  ]
}

Be precise and extract all relevant information. If information is missing, indicate it as null.
"""
```

### Example Prompts and Expected Outputs

#### Example 1: Create Employee (Norwegian)
**Input Prompt**: "Opprett en ansatt med navn Ola Nordmann, ola@example.org. Han skal være kontoadministrator."

**Expected LLM Output**:
```json
{
  "task_type": "create_employee",
  "language": "nb",
  "entities": {
    "employee": {
      "first_name": "Ola",
      "last_name": "Nordmann",
      "email": "ola@example.org"
    }
  },
  "special_instructions": {
    "role": "administrator"
  },
  "api_sequence": [
    {
      "endpoint": "/employee",
      "method": "POST",
      "data": {
        "firstName": "Ola",
        "lastName": "Nordmann",
        "email": "ola@example.org"
      }
    },
    {
      "endpoint": "/employee/{id}",
      "method": "PUT",
      "data": {
        "isAccountAdministrator": true
      }
    }
  ]
}
```

#### Example 2: Create Invoice (English)
**Input Prompt**: "Create an invoice for customer Acme AS with product 'Consulting' for 5000 NOK, due in 30 days."

**Expected LLM Output**:
```json
{
  "task_type": "create_invoice",
  "language": "en",
  "entities": {
    "customer": {
      "name": "Acme AS"
    },
    "invoice": {
      "due_days": 30,
      "line_items": [
        {
          "product_name": "Consulting",
          "amount": 5000,
          "currency": "NOK"
        }
      ]
    }
  },
  "api_sequence": [
    {
      "endpoint": "/customer",
      "method": "GET",
      "params": {"name": "Acme AS"},
      "purpose": "Find customer"
    },
    {
      "endpoint": "/product",
      "method": "GET",
      "params": {"name": "Consulting"},
      "purpose": "Find product"
    },
    {
      "endpoint": "/order",
      "method": "POST",
      "purpose": "Create order with line items"
    },
    {
      "endpoint": "/invoice",
      "method": "POST",
      "purpose": "Create invoice from order"
    }
  ]
}
```

## Code Implementation Patterns

### 1. Base Handler Class

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List
import logging

class BaseTaskHandler(ABC):
    """Base class for all task handlers"""
    
    def __init__(self, api_client, efficiency_tracker):
        self.api = api_client
        self.tracker = efficiency_tracker
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the task and return result"""
        pass
    
    def find_or_create_customer(self, name: str) -> Dict[str, Any]:
        """Helper: Find existing customer or create new one"""
        # Search first
        response = self.api.get("/customer", params={
            "name": name,
            "fields": "id,name,email",
            "count": 1
        })
        
        customers = response.json().get("values", [])
        if customers:
            self.logger.info(f"Found existing customer: {customers[0]['id']}")
            return customers[0]
        
        # Create if not found
        self.logger.info(f"Creating new customer: {name}")
        response = self.api.post("/customer", json={
            "name": name,
            "isCustomer": True
        })
        return response.json()["value"]
    
    def validate_required_fields(self, data: Dict, required: List[str]) -> None:
        """Validate that all required fields are present"""
        missing = [field for field in required if field not in data or data[field] is None]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")
```

### 2. Employee Handler (Tier 1)

```python
class EmployeeHandler(BaseTaskHandler):
    """Handle employee-related tasks"""
    
    def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        task_type = task_data["task_type"]
        
        if task_type == "create_employee":
            return self._create_employee(task_data)
        elif task_type == "update_employee":
            return self._update_employee(task_data)
        elif task_type == "delete_employee":
            return self._delete_employee(task_data)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    def _create_employee(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new employee"""
        employee_data = task_data["entities"]["employee"]
        
        # Validate required fields
        self.validate_required_fields(employee_data, ["first_name", "last_name", "email"])
        
        # Prepare API request
        payload = {
            "firstName": employee_data["first_name"],
            "lastName": employee_data["last_name"],
            "email": employee_data["email"]
        }
        
        # Optional fields
        if "phone" in employee_data:
            payload["phoneNumberMobile"] = employee_data["phone"]
        
        # Create employee
        self.logger.info(f"Creating employee: {employee_data['first_name']} {employee_data['last_name']}")
        response = self.api.post("/employee", json=payload)
        employee = response.json()["value"]
        employee_id = employee["id"]
        
        # Handle special instructions (e.g., administrator role)
        special = task_data.get("special_instructions", {})
        if special.get("role") == "administrator":
            self.logger.info(f"Setting administrator role for employee {employee_id}")
            self.api.put(f"/employee/{employee_id}", json={
                "isAccountAdministrator": True
            })
        
        return {
            "success": True,
            "employee_id": employee_id,
            "message": f"Created employee {employee_data['first_name']} {employee_data['last_name']}"
        }
```

### 3. Invoice Handler (Tier 2)

```python
class InvoiceHandler(BaseTaskHandler):
    """Handle invoice-related tasks"""
    
    def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        task_type = task_data["task_type"]
        
        if task_type == "create_invoice":
            return self._create_invoice(task_data)
        elif task_type == "create_payment":
            return self._create_payment(task_data)
        elif task_type == "create_credit_note":
            return self._create_credit_note(task_data)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    def _create_invoice(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create an invoice with line items"""
        from datetime import datetime, timedelta
        
        invoice_data = task_data["entities"]["invoice"]
        customer_data = task_data["entities"].get("customer", {})
        
        # Step 1: Find or create customer
        customer = self.find_or_create_customer(customer_data["name"])
        customer_id = customer["id"]
        
        # Step 2: Find or create products
        line_items = []
        for item in invoice_data.get("line_items", []):
            product = self._find_or_create_product(item["product_name"])
            line_items.append({
                "product": {"id": product["id"]},
                "count": item.get("quantity", 1),
                "unitPriceExcludingVatCurrency": item["amount"]
            })
        
        # Step 3: Create order
        today = datetime.now().strftime("%Y-%m-%d")
        order_payload = {
            "orderDate": today,
            "customer": {"id": customer_id},
            "orderLines": line_items
        }
        
        self.logger.info(f"Creating order for customer {customer_id}")
        order_response = self.api.post("/order", json=order_payload)
        order_id = order_response.json()["value"]["id"]
        
        # Step 4: Create invoice from order
        due_days = invoice_data.get("due_days", 30)
        due_date = (datetime.now() + timedelta(days=due_days)).strftime("%Y-%m-%d")
        
        invoice_payload = {
            "invoiceDate": today,
            "invoiceDueDate": due_date,
            "customer": {"id": customer_id},
            "orders": [{"id": order_id}]
        }
        
        self.logger.info(f"Creating invoice from order {order_id}")
        invoice_response = self.api.post("/invoice", json=invoice_payload)
        invoice_id = invoice_response.json()["value"]["id"]
        
        return {
            "success": True,
            "invoice_id": invoice_id,
            "order_id": order_id,
            "customer_id": customer_id,
            "message": f"Created invoice {invoice_id} for customer {customer['name']}"
        }
    
    def _find_or_create_product(self, name: str) -> Dict[str, Any]:
        """Helper: Find existing product or create new one"""
        # Search first
        response = self.api.get("/product", params={
            "name": name,
            "fields": "id,name",
            "count": 1
        })
        
        products = response.json().get("values", [])
        if products:
            return products[0]
        
        # Create if not found
        response = self.api.post("/product", json={
            "name": name,
            "number": f"PROD-{name[:10].upper()}"
        })
        return response.json()["value"]
```

### 4. Tripletex API Client

```python
import requests
from typing import Dict, Any, Optional
import logging

class TripletexClient:
    """Client for Tripletex API with authentication and error handling"""
    
    def __init__(self, base_url: str, session_token: str):
        self.base_url = base_url.rstrip("/")
        self.session_token = session_token
        self.auth = ("0", session_token)
        self.logger = logging.getLogger("TripletexClient")
        self.call_count = 0
        self.error_count = 0
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make an authenticated request to Tripletex API"""
        url = f"{self.base_url}{endpoint}"
        self.call_count += 1
        
        self.logger.debug(f"{method} {endpoint}")
        
        try:
            response = requests.request(
                method=method,
                url=url,
                auth=self.auth,
                timeout=30,
                **kwargs
            )
            
            # Track errors
            if 400 <= response.status_code < 500:
                self.error_count += 1
                self.logger.warning(f"4xx error: {response.status_code} - {response.text}")
            
            response.raise_for_status()
            return response
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {e}")
            raise
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> requests.Response:
        """GET request"""
        return self._make_request("GET", endpoint, params=params)
    
    def post(self, endpoint: str, json: Dict[str, Any]) -> requests.Response:
        """POST request"""
        return self._make_request("POST", endpoint, json=json)
    
    def put(self, endpoint: str, json: Dict[str, Any]) -> requests.Response:
        """PUT request"""
        return self._make_request("PUT", endpoint, json=json)
    
    def delete(self, endpoint: str) -> requests.Response:
        """DELETE request"""
        return self._make_request("DELETE", endpoint)
    
    def get_efficiency_stats(self) -> Dict[str, int]:
        """Get API call statistics"""
        return {
            "total_calls": self.call_count,
            "error_calls": self.error_count,
            "success_rate": (self.call_count - self.error_count) / self.call_count if self.call_count > 0 else 0
        }
```

### 5. Main FastAPI Application

```python
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import base64
import logging
from pathlib import Path

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TripletexAgent")

class FileAttachment(BaseModel):
    filename: str
    content_base64: str
    mime_type: str

class TripletexCredentials(BaseModel):
    base_url: str
    session_token: str

class SolveRequest(BaseModel):
    prompt: str
    files: Optional[List[FileAttachment]] = []
    tripletex_credentials: TripletexCredentials

@app.post("/solve")
async def solve(request: SolveRequest):
    """Main endpoint for solving Tripletex tasks"""
    try:
        logger.info(f"Received task: {request.prompt[:100]}...")
        
        # 1. Process files if any
        processed_files = []
        for file in request.files:
            file_data = base64.b64decode(file.content_base64)
            file_path = Path(f"/tmp/{file.filename}")
            file_path.write_bytes(file_data)
            processed_files.append({
                "filename": file.filename,
                "path": str(file_path),
                "mime_type": file.mime_type
            })
            logger.info(f"Processed file: {file.filename}")
        
        # 2. Initialize Tripletex client
        api_client = TripletexClient(
            base_url=request.tripletex_credentials.base_url,
            session_token=request.tripletex_credentials.session_token
        )
        
        # 3. Analyze prompt with LLM
        task_analysis = analyze_prompt_with_llm(request.prompt, processed_files)
        logger.info(f"Task analysis: {task_analysis['task_type']}")
        
        # 4. Route to appropriate handler
        handler = get_handler(task_analysis["task_type"], api_client)
        result = handler.execute(task_analysis)
        
        # 5. Log efficiency stats
        stats = api_client.get_efficiency_stats()
        logger.info(f"Completed with {stats['total_calls']} API calls, {stats['error_calls']} errors")
        
        return JSONResponse({"status": "completed"})
        
    except Exception as e:
        logger.error(f"Task failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

def analyze_prompt_with_llm(prompt: str, files: List[Dict]) -> Dict[str, Any]:
    """Use LLM to analyze the prompt and extract task information"""
    # TODO: Implement LLM integration (OpenAI, Claude, etc.)
    # This is a placeholder
    pass

def get_handler(task_type: str, api_client):
    """Get the appropriate handler for the task type"""
    handlers = {
        "create_employee": EmployeeHandler,
        "create_customer": CustomerHandler,
        "create_invoice": InvoiceHandler,
        # ... more handlers
    }
    
    handler_class = handlers.get(task_type)
    if not handler_class:
        raise ValueError(f"No handler for task type: {task_type}")
    
    return handler_class(api_client, efficiency_tracker=None)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Efficiency Optimization Strategies

### 1. Pre-flight Validation

```python
def validate_before_post(data: Dict, required_fields: List[str]) -> bool:
    """Validate data before making API call to avoid 422 errors"""
    for field in required_fields:
        if field not in data or data[field] is None:
            return False
    return True

# Example usage
if validate_before_post(employee_data, ["firstName", "lastName", "email"]):
    response = api.post("/employee", json=employee_data)
else:
    raise ValueError("Missing required fields")
```

### 2. Response Caching

```python
class CachedTripletexClient(TripletexClient):
    """Client with response caching to avoid redundant GET requests"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache = {}
    
    def get_cached(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """GET with caching"""
        cache_key = f"{endpoint}:{str(params)}"
        
        if cache_key in self.cache:
            self.logger.debug(f"Cache hit: {cache_key}")
            return self.cache[cache_key]
        
        response = self.get(endpoint, params=params)
        result = response.json()
        self.cache[cache_key] = result
        return result
```

### 3. Smart Error Recovery

```python
def smart_retry(api_call, max_retries=1):
    """Retry with error message parsing"""
    try:
        return api_call()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 422:
            # Parse error message
            error_data = e.response.json()
            error_msg = error_data.get("message", "")
            
            # Extract what's wrong and fix it
            if "required" in error_msg.lower():
                # Identify missing field and add it
                pass
            elif "invalid" in error_msg.lower():
                # Fix invalid value
                pass
            
            # Retry once with fix
            if max_retries > 0:
                return smart_retry(api_call, max_retries - 1)
        raise
```

## Testing Strategy

### Unit Test Example

```python
import pytest
from unittest.mock import Mock, MagicMock

def test_create_employee_handler():
    """Test employee creation"""
    # Mock API client
    api_client = Mock()
    api_client.post.return_value = MagicMock(
        json=lambda: {"value": {"id": 123}}
    )
    
    # Create handler
    handler = EmployeeHandler(api_client, None)
    
    # Test data
    task_data = {
        "task_type": "create_employee",
        "entities": {
            "employee": {
                "first_name": "Ola",
                "last_name": "Nordmann",
                "email": "ola@example.org"
            }
        },
        "special_instructions": {
            "role": "administrator"
        }
    }
    
    # Execute
    result = handler.execute(task_data)
    
    # Verify
    assert result["success"] is True
    assert result["employee_id"] == 123
    assert api_client.post.call_count == 1
    assert api_client.put.call_count == 1
```

## Deployment Checklist

- [ ] Environment variables configured (API keys, etc.)
- [ ] HTTPS endpoint accessible
- [ ] Health check endpoint (`/health`)
- [ ] Logging configured
- [ ] Error handling tested
- [ ] Timeout handling (5 min limit)
- [ ] All handlers implemented
- [ ] LLM integration working
- [ ] File processing tested
- [ ] Sandbox testing passed
- [ ] Efficiency tracking enabled
- [ ] Documentation complete

## Monitoring and Debugging

### Key Metrics to Track
1. **API Call Count**: Total calls per task
2. **Error Rate**: 4xx errors / total calls
3. **Execution Time**: Time to complete task
4. **Success Rate**: Tasks completed / tasks attempted
5. **Score Progression**: Track scores over time

### Logging Best Practices
```python
# Log at different levels
logger.debug("Detailed information for debugging")
logger.info("General information about task progress")
logger.warning("Potential issues (e.g., 4xx errors)")
logger.error("Serious problems that need attention")

# Include context
logger.info(f"Creating employee: {first_name} {last_name} (email: {email})")
logger.warning(f"API error {status_code}: {error_message}")