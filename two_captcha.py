from typing import Dict, Any, Optional
import requests
from .captcha_solver import CaptchaSolverBase, CaptchaSolverError

class TwoCaptcha(CaptchaSolverBase):
    """2captcha.com API implementation"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.base_url = 'https://2captcha.com/in.php'
        self.result_url = 'https://2captcha.com/res.php'

    def solve_captcha(self, captcha_type: str, **kwargs) -> str:
        """Solve various types of captchas using 2captcha service

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
        params = {
            'key': self.api_key,
            'method': 'post',
            'json': 1
        }

        files = None
        if image_path:
            files = {'file': open(image_path, 'rb')}
        elif image_url:
            params['method'] = 'base64'
            params['body'] = image_url
        else:
            raise CaptchaSolverError('Either image_path or image_url must be provided')

        response = requests.post(self.base_url, params=params, files=files)
        data = self._handle_response(response)

        if data.get('status') == 1:
            return self._get_task_result(data['request'])
        else:
            raise CaptchaSolverError(f"Failed to submit image captcha: {data.get('error_text')}")

    def _solve_recaptcha_v2(self, site_key: str, page_url: str, **kwargs) -> str:
        """Solve reCAPTCHA v2"""
        params = {
            'key': self.api_key,
            'method': 'userrecaptcha',
            'googlekey': site_key,
            'pageurl': page_url,
            'json': 1
        }

        response = requests.get(self.base_url, params=params)
        data = self._handle_response(response)

        if data.get('status') == 1:
            return self._get_task_result(data['request'])
        else:
            raise CaptchaSolverError(f"Failed to submit reCAPTCHA v2: {data.get('error_text')}")

    def _solve_recaptcha_v3(self, site_key: str, page_url: str, action: str, min_score: float = 0.7, **kwargs) -> str:
        """Solve reCAPTCHA v3"""
        params = {
            'key': self.api_key,
            'method': 'userrecaptcha',
            'version': 'v3',
            'googlekey': site_key,
            'pageurl': page_url,
            'action': action,
            'min_score': min_score,
            'json': 1
        }

        response = requests.get(self.base_url, params=params)
        data = self._handle_response(response)

        if data.get('status') == 1:
            return self._get_task_result(data['request'])
        else:
            raise CaptchaSolverError(f"Failed to submit reCAPTCHA v3: {data.get('error_text')}")

    def _solve_hcaptcha(self, site_key: str, page_url: str, **kwargs) -> str:
        """Solve hCaptcha"""
        params = {
            'key': self.api_key,
            'method': 'hcaptcha',
            'sitekey': site_key,
            'pageurl': page_url,
            'json': 1
        }

        response = requests.get(self.base_url, params=params)
        data = self._handle_response(response)

        if data.get('status') == 1:
            return self._get_task_result(data['request'])
        else:
            raise CaptchaSolverError(f"Failed to submit hCaptcha: {data.get('error_text')}")

    def _get_task_result(self, task_id: str) -> str:
        """Get solution for submitted captcha task"""
        def get_result(task_id: str) -> Optional[str]:
            params = {
                'key': self.api_key,
                'action': 'get',
                'id': task_id,
                'json': 1
            }

            response = requests.get(self.result_url, params=params)
            data = self._handle_response(response)

            if data.get('status') == 1:
                return data.get('request')
            elif data.get('request') == 'CAPCHA_NOT_READY':
                return None
            else:
                raise CaptchaSolverError(f"Error getting result: {data.get('request')}")

        return self._wait_for_result(task_id, get_result)

    def get_balance(self) -> float:
        """Get current account balance"""
        params = {
            'key': self.api_key,
            'action': 'getbalance',
            'json': 1
        }

        response = requests.get(self.result_url, params=params)
        data = self._handle_response(response)

        if data.get('status') == 1:
            return float(data.get('request', 0))
        else:
            raise CaptchaSolverError(f"Failed to get balance: {data.get('error_text')}")