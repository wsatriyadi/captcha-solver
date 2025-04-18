from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import time
import requests

class CaptchaSolverError(Exception):
    """Base exception for captcha solver errors"""
    pass

class CaptchaSolverBase(ABC):
    """Base class for captcha solving services"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.timeout = 120  # Default timeout in seconds
        self.polling_interval = 5  # Default polling interval in seconds

    @abstractmethod
    def solve_captcha(self, captcha_type: str, **kwargs) -> str:
        """Solve the captcha and return the solution"""
        pass

    @abstractmethod
    def get_balance(self) -> float:
        """Get current account balance"""
        pass

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response and check for errors"""
        try:
            data = response.json()
        except ValueError:
            raise CaptchaSolverError(f"Invalid JSON response: {response.text}")

        if response.status_code != 200:
            raise CaptchaSolverError(f"API request failed: {response.status_code} - {response.text}")

        return data

    def _wait_for_result(self, task_id: str, get_result_func) -> str:
        """Wait for captcha solving result"""
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                result = get_result_func(task_id)
                if result:
                    return result
            except Exception as e:
                raise CaptchaSolverError(f"Error while waiting for result: {str(e)}")
            
            time.sleep(self.polling_interval)
        
        raise CaptchaSolverError("Timeout waiting for captcha solution")