from typing import Dict, Any, Optional
import requests
import base64
from .captcha_solver import CaptchaSolverBase, CaptchaSolverError

class DeathByCaptcha(CaptchaSolverBase):
    """deathbycaptcha.com API implementation"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.username, self.password = api_key.split(':')
        self.base_url = 'https://api.dbcapi.me/api'

    def solve_captcha(self, captcha_type: str, **kwargs) -> str:
        """Solve various types of captchas using DeathByCaptcha service

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

    def _solve_image_captcha(self, image_path: Optional[str] = None, image_url: Optional[str] = None, **kwargs) -> str:
        """Solve regular image captcha"""
        if image_path:
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
        elif image_url:
            response = requests.get(image_url)
            image_data = base64.b64encode(response.content).decode('utf-8')
        else:
            raise CaptchaSolverError('Either image_path or image_url must be provided')

        data = {
            'username': self.username,
            'password': self.password,
            'captchafile': image_data
        }

        response = requests.post(f'{self.base_url}/captcha', data=data)
        result = self._handle_response(response)

        if 'captcha' in result:
            return self._get_task_result(str(result['captcha']))
        else:
            raise CaptchaSolverError(f"Failed to submit image captcha: {result.get('error')}")

    def _solve_recaptcha_v2(self, site_key: str, page_url: str, **kwargs) -> str:
        """Solve reCAPTCHA v2"""
        data = {
            'username': self.username,
            'password': self.password,
            'type': 4,
            'token_params': {
                'googlekey': site_key,
                'pageurl': page_url
            }
        }

        response = requests.post(f'{self.base_url}/captcha', json=data)
        result = self._handle_response(response)

        if 'captcha' in result:
            return self._get_task_result(str(result['captcha']))
        else:
            raise CaptchaSolverError(f"Failed to submit reCAPTCHA v2: {result.get('error')}")

    def _solve_recaptcha_v3(self, site_key: str, page_url: str, action: str, min_score: float = 0.7, **kwargs) -> str:
        """Solve reCAPTCHA v3"""
        data = {
            'username': self.username,
            'password': self.password,
            'type': 4,
            'token_params': {
                'googlekey': site_key,
                'pageurl': page_url,
                'action': action,
                'min_score': min_score,
                'version': 'v3'
            }
        }

        response = requests.post(f'{self.base_url}/captcha', json=data)
        result = self._handle_response(response)

        if 'captcha' in result:
            return self._get_task_result(str(result['captcha']))
        else:
            raise CaptchaSolverError(f"Failed to submit reCAPTCHA v3: {result.get('error')}")

    def _solve_hcaptcha(self, site_key: str, page_url: str, **kwargs) -> str:
        """Solve hCaptcha"""
        data = {
            'username': self.username,
            'password': self.password,
            'type': 7,
            'token_params': {
                'sitekey': site_key,
                'pageurl': page_url
            }
        }

        response = requests.post(f'{self.base_url}/captcha', json=data)
        result = self._handle_response(response)

        if 'captcha' in result:
            return self._get_task_result(str(result['captcha']))
        else:
            raise CaptchaSolverError(f"Failed to submit hCaptcha: {result.get('error')}")

    def _get_task_result(self, task_id: str) -> str:
        """Get solution for submitted captcha task"""
        def get_result(task_id: str) -> Optional[str]:
            response = requests.get(
                f'{self.base_url}/captcha/{task_id}',
                params={'username': self.username, 'password': self.password}
            )
            result = self._handle_response(response)

            if result.get('is_correct'):
                if 'text' in result:
                    return result['text']
                elif 'token' in result:
                    return result['token']
                else:
                    raise CaptchaSolverError("Unknown solution format")
            elif not result.get('status') == 0:
                raise CaptchaSolverError(f"Error getting result: {result.get('error')}")
            return None

        return self._wait_for_result(task_id, get_result)

    def get_balance(self) -> float:
        """Get current account balance in US cents"""
        response = requests.post(
            f'{self.base_url}/user',
            data={'username': self.username, 'password': self.password}
        )
        result = self._handle_response(response)

        if 'balance' in result:
            return float(result['balance']) / 100  # Convert cents to dollars
        else:
            raise CaptchaSolverError(f"Failed to get balance: {result.get('error')}")