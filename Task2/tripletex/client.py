"""
Tripletex API Client with authentication and error handling
"""

import requests
from typing import Dict, Any, Optional
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)


class TripletexAPIError(Exception):
    """Custom exception for Tripletex API errors"""
    pass


class TripletexClient:
    """Client for Tripletex API with authentication and retry logic"""
    
    def __init__(self, base_url: str, session_token: str):
        """
        Initialize Tripletex API client
        
        Args:
            base_url: Tripletex API base URL (proxy URL from competition)
            session_token: Session token for authentication
        """
        self.base_url = base_url.rstrip("/")
        self.session_token = session_token
        self.auth = ("0", session_token)  # Username is always "0"
        self.session = requests.Session()
        self.session.auth = self.auth
        
        # Efficiency tracking
        self.call_count = 0
        self.error_count = 0
        self.calls_log = []
    
    def _log_call(self, method: str, endpoint: str, status_code: int, error: bool = False):
        """Log API call for efficiency tracking"""
        self.call_count += 1
        if error:
            self.error_count += 1
        
        self.calls_log.append({
            "method": method,
            "endpoint": endpoint,
            "status_code": status_code,
            "error": error
        })
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(requests.exceptions.RequestException),
        reraise=True
    )
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json: Optional[Dict] = None,
        timeout: int = 30
    ) -> requests.Response:
        """
        Make an authenticated request to Tripletex API with retry logic
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            params: Query parameters
            json: JSON body for POST/PUT
            timeout: Request timeout in seconds
            
        Returns:
            Response object
            
        Raises:
            TripletexAPIError: If request fails after retries
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            logger.debug(f"{method} {endpoint}")
            
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json,
                timeout=timeout
            )
            
            # Log the call
            is_error = 400 <= response.status_code < 600
            self._log_call(method, endpoint, response.status_code, is_error)
            
            if is_error:
                error_msg = f"{method} {endpoint} failed with status {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f": {error_data.get('message', response.text)}"
                except:
                    error_msg += f": {response.text}"
                
                logger.warning(error_msg)
            
            response.raise_for_status()
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {method} {endpoint} - {str(e)}")
            raise TripletexAPIError(f"API request failed: {str(e)}")
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        GET request
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            JSON response as dictionary
        """
        response = self._make_request("GET", endpoint, params=params)
        return response.json()
    
    def post(self, endpoint: str, json: Dict[str, Any]) -> Dict[str, Any]:
        """
        POST request
        
        Args:
            endpoint: API endpoint path
            json: Request body
            
        Returns:
            JSON response as dictionary
        """
        response = self._make_request("POST", endpoint, json=json)
        return response.json()
    
    def put(self, endpoint: str, json: Dict[str, Any]) -> Dict[str, Any]:
        """
        PUT request
        
        Args:
            endpoint: API endpoint path
            json: Request body
            
        Returns:
            JSON response as dictionary
        """
        response = self._make_request("PUT", endpoint, json=json)
        return response.json()
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """
        DELETE request
        
        Args:
            endpoint: API endpoint path
            
        Returns:
            JSON response as dictionary
        """
        response = self._make_request("DELETE", endpoint)
        try:
            return response.json()
        except:
            return {"status": "deleted"}
    
    def get_efficiency_stats(self) -> Dict[str, Any]:
        """
        Get API call efficiency statistics
        
        Returns:
            Dictionary with call statistics
        """
        return {
            "total_calls": self.call_count,
            "error_calls": self.error_count,
            "success_calls": self.call_count - self.error_count,
            "success_rate": (self.call_count - self.error_count) / self.call_count if self.call_count > 0 else 0,
            "calls_log": self.calls_log
        }

# Made with Bob
