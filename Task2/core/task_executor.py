"""
Task Executor - Executes API calls based on LLM analysis
"""

import logging
from typing import Dict, Any, List
from tripletex.client import TripletexClient

logger = logging.getLogger(__name__)


class TaskExecutor:
    """Executes Tripletex API calls based on task analysis"""
    
    def __init__(self, client: TripletexClient):
        """
        Initialize task executor
        
        Args:
            client: Tripletex API client
        """
        self.client = client
        self.execution_context = {}  # Store results from previous steps
    
    def execute_task(self, task_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task based on LLM analysis
        
        Args:
            task_analysis: Structured task analysis from LLM
            
        Returns:
            Execution result with status and details
        """
        try:
            api_calls = task_analysis.get("api_calls", [])
            
            if not api_calls:
                # Fallback: try to infer API calls from task_type
                api_calls = self._infer_api_calls(task_analysis)
            
            logger.info(f"Executing {len(api_calls)} API calls for task: {task_analysis.get('task_type')}")
            
            results = []
            for call in api_calls:
                result = self._execute_api_call(call)
                results.append(result)
            
            return {
                "status": "success",
                "task_type": task_analysis.get("task_type"),
                "results": results,
                "explanation": task_analysis.get("explanation", "Task completed successfully"),
                "efficiency": self.client.get_efficiency_stats()
            }
            
        except Exception as e:
            logger.error(f"Task execution failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "task_type": task_analysis.get("task_type"),
                "efficiency": self.client.get_efficiency_stats()
            }
    
    def _execute_api_call(self, call: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single API call
        
        Args:
            call: API call specification
            
        Returns:
            Call result
        """
        step = call.get("step", 0)
        endpoint = call.get("endpoint", "")
        method = call.get("method", "GET").upper()
        purpose = call.get("purpose", "")
        data = call.get("data", {})
        params = call.get("params", {})
        save_as = call.get("save_response_as")
        
        logger.info(f"Step {step}: {method} {endpoint} - {purpose}")
        
        # Replace placeholders in endpoint with saved values
        endpoint = self._resolve_placeholders(endpoint)
        
        # Replace placeholders in data
        data = self._resolve_placeholders(data)
        
        try:
            # Execute the API call
            if method == "GET":
                response = self.client.get(endpoint, params=params)
            elif method == "POST":
                response = self.client.post(endpoint, json=data)
            elif method == "PUT":
                response = self.client.put(endpoint, json=data)
            elif method == "DELETE":
                response = self.client.delete(endpoint)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Save response if requested
            if save_as and response:
                if "value" in response:
                    # Single entity response
                    self.execution_context[save_as] = response["value"].get("id")
                elif "values" in response and response["values"]:
                    # List response - save first item's ID
                    self.execution_context[save_as] = response["values"][0].get("id")
                else:
                    # Save entire response
                    self.execution_context[save_as] = response
                
                logger.debug(f"Saved {save_as} = {self.execution_context[save_as]}")
            
            return {
                "step": step,
                "status": "success",
                "purpose": purpose,
                "response": response
            }
            
        except Exception as e:
            logger.error(f"Step {step} failed: {str(e)}")
            return {
                "step": step,
                "status": "error",
                "purpose": purpose,
                "error": str(e)
            }
    
    def _resolve_placeholders(self, obj: Any) -> Any:
        """
        Recursively resolve placeholders like {employee_id} with saved values
        
        Args:
            obj: Object to resolve (string, dict, list, etc.)
            
        Returns:
            Resolved object
        """
        if isinstance(obj, str):
            # Replace {variable} with saved value
            for key, value in self.execution_context.items():
                placeholder = f"{{{key}}}"
                if placeholder in obj:
                    obj = obj.replace(placeholder, str(value))
            return obj
        
        elif isinstance(obj, dict):
            return {k: self._resolve_placeholders(v) for k, v in obj.items()}
        
        elif isinstance(obj, list):
            return [self._resolve_placeholders(item) for item in obj]
        
        else:
            return obj
    
    def _infer_api_calls(self, task_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Infer API calls from task type when LLM doesn't provide them
        
        Args:
            task_analysis: Task analysis
            
        Returns:
            List of API calls
        """
        task_type = task_analysis.get("task_type", "")
        entities = task_analysis.get("entities", {})
        special = task_analysis.get("special_instructions", {})
        
        calls = []
        
        # Employee tasks
        if task_type == "create_employee" and "employee" in entities:
            emp = entities["employee"]
            calls.append({
                "step": 1,
                "endpoint": "/employee",
                "method": "POST",
                "purpose": "Create employee",
                "data": emp,
                "save_response_as": "employee_id"
            })
            
            if special.get("is_administrator"):
                calls.append({
                    "step": 2,
                    "endpoint": "/employee/{employee_id}",
                    "method": "PUT",
                    "purpose": "Set administrator role",
                    "data": {"isAccountAdministrator": True}
                })
        
        # Customer tasks
        elif task_type == "create_customer" and "customer" in entities:
            cust = entities["customer"]
            cust["isCustomer"] = True
            calls.append({
                "step": 1,
                "endpoint": "/customer",
                "method": "POST",
                "purpose": "Create customer",
                "data": cust,
                "save_response_as": "customer_id"
            })
        
        # Supplier tasks
        elif task_type == "create_supplier" and "supplier" in entities:
            supp = entities["supplier"]
            supp["isSupplier"] = True
            calls.append({
                "step": 1,
                "endpoint": "/customer",
                "method": "POST",
                "purpose": "Create supplier",
                "data": supp,
                "save_response_as": "supplier_id"
            })
        
        # Product tasks
        elif task_type == "create_product" and "product" in entities:
            prod = entities["product"]
            calls.append({
                "step": 1,
                "endpoint": "/product",
                "method": "POST",
                "purpose": "Create product",
                "data": prod,
                "save_response_as": "product_id"
            })
        
        return calls

# Made with Bob
