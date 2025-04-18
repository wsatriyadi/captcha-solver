from typing import List, Dict, Any, Optional
from .captcha_solver import CaptchaSolverBase, CaptchaSolverError
from .two_captcha import TwoCaptcha
from .anti_captcha import AntiCaptcha
from .death_by_captcha import DeathByCaptcha

class CaptchaSolver:
    """Unified captcha solver that manages multiple services with automatic fallback"""

    def __init__(self, service_configs: List[Dict[str, str]]):
        """Initialize CaptchaSolver with multiple service configurations

        Args:
            service_configs: List of dictionaries containing service configurations
                Each dict should have:
                - 'service': Service name ('2captcha', 'anti-captcha', 'deathbycaptcha')
                - 'api_key': API key for the service
        """
        self.solvers = []
        for config in service_configs:
            service = config['service'].lower()
            api_key = config['api_key']

            if service == '2captcha':
                self.solvers.append(TwoCaptcha(api_key))
            elif service == 'anti-captcha':
                self.solvers.append(AntiCaptcha(api_key))
            elif service == 'deathbycaptcha':
                self.solvers.append(DeathByCaptcha(api_key))

        if not self.solvers:
            raise ValueError("No valid services configured")

    def solve_captcha(self, captcha_type: str, **kwargs) -> str:
        """Solve captcha using configured services with automatic fallback

        Args:
            captcha_type: Type of captcha ('image', 'recaptcha_v2', 'recaptcha_v3', 'hcaptcha')
            **kwargs: Additional parameters specific to captcha type

        Returns:
            str: Solved captcha text or token

        Raises:
            CaptchaSolverError: If all services fail to solve the captcha
        """
        last_error = None
        for solver in self.solvers:
            try:
                return solver.solve_captcha(captcha_type, **kwargs)
            except Exception as e:
                last_error = e
                continue

        raise CaptchaSolverError(f"All services failed to solve captcha. Last error: {str(last_error)}")

    def get_balances(self) -> Dict[str, float]:
        """Get account balances for all configured services

        Returns:
            Dict[str, float]: Dictionary mapping service names to their balances
        """
        balances = {}
        for solver in self.solvers:
            try:
                service_name = solver.__class__.__name__
                balances[service_name] = solver.get_balance()
            except Exception as e:
                balances[solver.__class__.__name__] = f"Error: {str(e)}"
        return balances