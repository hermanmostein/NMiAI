"""
LLM Service for interpreting accounting task prompts
"""

import json
import logging
from typing import Dict, Any, List, Optional
from openai import OpenAI
from config.settings import settings

logger = logging.getLogger(__name__)


class LLMService:
    """Service for using OpenAI to interpret task prompts"""
    
    def __init__(self):
        """Initialize OpenAI client"""
        if not settings.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY not set - LLM service will not work")
            self.client = None
        else:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
    
    def analyze_prompt(self, prompt: str, files: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Analyze a task prompt and generate structured API call plan
        
        Args:
            prompt: Natural language task description
            files: Optional list of processed files with extracted data
            
        Returns:
            Structured task analysis with API calls to execute
        """
        if not self.client:
            raise ValueError("OPENAI_API_KEY not configured. Set it in environment variables.")
        
        system_prompt = self._get_system_prompt()
        user_message = self._build_user_message(prompt, files)
        
        try:
            logger.info(f"Analyzing prompt with {self.model}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.1,  # Low temperature for consistent, deterministic output
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            logger.info(f"Task analysis complete: {result.get('task_type', 'unknown')}")
            
            return result
            
        except Exception as e:
            logger.error(f"LLM analysis failed: {str(e)}")
            raise
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for task analysis"""
        return """You are an expert at analyzing accounting task prompts for the Tripletex API.

Your job is to:
1. Understand the task from natural language in ANY of these languages: Norwegian (nb/nn), English, Spanish, Portuguese, German, French, Swedish, Danish
2. Determine what Tripletex API calls are needed
3. Extract all relevant data from the prompt
4. Generate a structured execution plan

IMPORTANT: Return ONLY valid JSON with this exact structure:

{
  "task_type": "one of: create_employee, update_employee, create_customer, update_customer, create_supplier, create_product, create_invoice, create_order, register_payment, create_credit_note, create_travel_expense, delete_travel_expense, create_project, create_department, create_voucher, delete_voucher, bank_reconciliation, or general",
  "language": "detected language code (nb, en, es, pt, de, fr, sv, da, nn)",
  "confidence": 0.95,
  "entities": {
    "employee": {"firstName": "...", "lastName": "...", "email": "..."},
    "customer": {"name": "...", "email": "...", "organizationNumber": "..."},
    "supplier": {"name": "...", "email": "..."},
    "product": {"name": "...", "number": "...", "price": 0},
    "invoice": {"invoiceDate": "YYYY-MM-DD", "dueDate": "YYYY-MM-DD", "orderLines": [...]},
    "payment": {"amount": 0, "date": "YYYY-MM-DD"},
    "project": {"name": "...", "number": "..."},
    "department": {"name": "...", "number": "..."},
    "voucher": {"date": "YYYY-MM-DD", "description": "..."},
    "travel_expense": {"travelDetails": "..."}
  },
  "relationships": {
    "customer_id": "reference to customer",
    "project_customer": "link project to customer",
    "invoice_customer": "link invoice to customer"
  },
  "special_instructions": {
    "is_administrator": true,
    "enable_module": "accounting",
    "set_permissions": ["read", "write"]
  },
  "api_calls": [
    {
      "step": 1,
      "endpoint": "/employee",
      "method": "POST",
      "purpose": "Create employee",
      "data": {"firstName": "...", "lastName": "...", "email": "..."},
      "save_response_as": "employee_id"
    },
    {
      "step": 2,
      "endpoint": "/employee/{employee_id}",
      "method": "PUT",
      "purpose": "Set administrator role",
      "data": {"isAccountAdministrator": true},
      "depends_on": ["employee_id"]
    }
  ],
  "validation": {
    "required_fields": ["firstName", "lastName", "email"],
    "expected_result": "Employee created with administrator role"
  },
  "explanation": "Clear explanation of what will be done"
}

CRITICAL RULES:
1. Always include ALL fields shown above, even if empty/null
2. For dates, use ISO format YYYY-MM-DD
3. Extract ALL entities mentioned in the prompt
4. Plan API calls in correct dependency order
5. Include validation criteria
6. Provide clear explanation
7. Handle ambiguous prompts gracefully
8. If information is missing, use reasonable defaults or mark as null
9. For multi-step tasks, ensure proper sequencing
10. Consider error cases and provide fallback strategies

COMMON PATTERNS:
- Create employee: POST /employee, optionally PUT /employee/{id} for roles
- Create customer: POST /customer with isCustomer=true
- Create supplier: POST /customer with isSupplier=true
- Create invoice: GET/POST /customer, GET/POST /product, POST /order, POST /invoice
- Register payment: POST /payment with invoice reference
- Create project: POST /project with customer reference
- Travel expense: POST /travelExpense or DELETE /travelExpense/{id}

Remember: Return ONLY the JSON object, no other text."""
    
    def _build_user_message(self, prompt: str, files: Optional[List[Dict]] = None) -> str:
        """Build the user message with prompt and file data"""
        message = f"Task prompt:\n{prompt}\n\n"
        
        if files:
            message += "Attached files:\n"
            for file in files:
                message += f"- {file['filename']} ({file['mime_type']})\n"
                if 'extracted_text' in file:
                    message += f"  Extracted text: {file['extracted_text'][:500]}...\n"
                if 'extracted_data' in file:
                    message += f"  Extracted data: {json.dumps(file['extracted_data'])}\n"
        
        message += "\nAnalyze this task and return the structured JSON response."
        return message

# Made with Bob
