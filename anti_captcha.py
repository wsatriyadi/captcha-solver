from typing import Dict, Any, Optional
import requests
from .captcha_solver import CaptchaSolverBase, CaptchaSolverError

class AntiCaptcha(CaptchaSolverBase):
    """anti-captcha.com API implementation"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.base_url = 'https://api.anti-captcha.com'

    def solve_captcha(self, captcha_type: str, **kwargs) -> str:
        """Solve various types of captchas using Anti-Captcha service

        Args:
            captcha_type: Type of captcha ('image', 'recaptcha_v2', 'recaptcha_v3', 'hcaptcha')
            **kwargs: Additional parameters specific to captcha type

        Returns:
            str: Solved captcha text or token
        """
        if captcha_type == 'image':
            return self._solve_image_captcha(**kwargs)
        elif captcha_type == 'recaptcha_v2':
            return self._solve_recaptcha_v2(**kwargs)
        elif captcha_type == 'recaptcha_v3':
            return self._solve_recaptcha_v3(**kwargs)
        elif captcha_type == 'hcaptcha':
            return self._solve_hcaptcha(**kwargs)
        else:
            raise CaptchaSolverError(f'Unsupported captcha type: {captcha_type}')

    def _create_task(self, task_data: Dict[str, Any]) -> str:
        """Create a new captcha solving task"""
        data = {
            'clientKey': self.api_key,
            'task': task_data
        }

        response = requests.post(f'{self.base_url}/createTask', json=data)
        result = self._handle_response(response)

        if result.get('errorId') > 0:
            raise CaptchaSolverError(f"Failed to create task: {result.get('errorDescription')}")

        return str(result.get('taskId'))

    def _solve_image_captcha(self, image_path: Optional[str] = None, image_url: Optional[str] = None, **kwargs) -> str:
        """Solve regular image captcha"""
        if image_path:
            with open(image_path, 'rb') as f:
                image_data = f.read()
            task = {
                'type': 'ImageToTextTask',
                'body': image_data.encode('base64').decode('utf-8')
            }
        elif image_url:
            task = {
                'type': 'ImageToTextTask',
                'imageUrl': image_url
            }
        else:
            raise CaptchaSolverError('Either image_path or image_url must be provided')

        task_id = self._create_task(task)
        return self._get_task_result(task_id)

    def _solve_recaptcha_v2(self, site_key: str, page_url: str, **kwargs) -> str:
        """Solve reCAPTCHA v2"""
        task = {
            'type': 'RecaptchaV2TaskProxyless',
            'websiteURL': page_url,
            'websiteKey': site_key
        }

        task_id = self._create_task(task)
        return self._get_task_result(task_id)

    def _solve_recaptcha_v3(self, site_key: str, page_url: str, action: str, min_score: float = 0.7, **kwargs) -> str:
        """Solve reCAPTCHA v3"""
        task = {
            'type': 'RecaptchaV3TaskProxyless',
            'websiteURL': page_url,
            'websiteKey': site_key,
            'minScore': min_score,
            'pageAction': action
        }

        task_id = self._create_task(task)
        return self._get_task_result(task_id)

    def _solve_hcaptcha(self, site_key: str, page_url: str, **kwargs) -> str:
        """Solve hCaptcha"""
        task = {
            'type': 'HCaptchaTaskProxyless',
            'websiteURL': page_url,
            'websiteKey': site_key
        }

        task_id = self._create_task(task)
        return self._get_task_result(task_id)

    def _get_task_result(self, task_id: str) -> str:
        """Get solution for submitted captcha task"""
        def get_result(task_id: str) -> Optional[str]:
            data = {
                'clientKey': self.api_key,
                'taskId': int(task_id)
            }

            response = requests.post(f'{self.base_url}/getTaskResult', json=data)
            result = self._handle_response(response)

            if result.get('errorId') > 0:
                raise CaptchaSolverError(f"Error getting result: {result.get('errorDescription')}")

            if result.get('status') == 'ready':
                solution = result.get('solution', {})
                if 'text' in solution:
                    return solution['text']
                elif 'gRecaptchaResponse' in solution:
                    return solution['gRecaptchaResponse']
                elif 'token' in solution:
                    return solution['token']
                else:
                    raise CaptchaSolverError("Unknown solution format")
            return None

        return self._wait_for_result(task_id, get_result)

    def get_balance(self) -> float:
        """Get current account balance"""
        data = {
            'clientKey': self.api_key
        }

        response = requests.post(f'{self.base_url}/getBalance', json=data)
        result = self._handle_response(response)

        if result.get('errorId') > 0:
            raise CaptchaSolverError(f"Failed to get balance: {result.get('errorDescription')}")

        return float(result.get('balance', 0))