# Python Captcha Solver

A comprehensive Python module for solving various types of captchas using multiple popular captcha solving services. This module provides a unified interface to work with 2captcha, Anti-Captcha, and DeathByCaptcha services with automatic fallback functionality.

## Features

- Support for multiple captcha solving services
- Automatic fallback if one service fails
- Unified interface for all services
- Support for various captcha types:
  - Regular image captchas
  - reCAPTCHA v2
  - reCAPTCHA v3
  - hCaptcha

## Installation

```bash
pip install requests
```

## Usage

### Basic Usage

```python
from captcha_solver import CaptchaSolver

# Configure multiple services
services = [
    {
        'service': '2captcha',
        'api_key': 'your_2captcha_api_key'
    },
    {
        'service': 'anti-captcha',
        'api_key': 'your_anti_captcha_api_key'
    },
    {
        'service': 'deathbycaptcha',
        'api_key': 'username:password'  # DBC uses username:password format
    }
]

# Initialize the solver
solver = CaptchaSolver(services)

# Solve an image captcha
result = solver.solve_captcha('image', image_path='path/to/captcha.png')
print(f'Solved captcha: {result}')

# Get account balances
balances = solver.get_balances()
print('Service balances:', balances)
```

### Solving Different Captcha Types

#### Image Captcha
```python
# Using local file
result = solver.solve_captcha('image', image_path='captcha.png')

# Using URL
result = solver.solve_captcha('image', image_url='https://example.com/captcha.png')
```

#### ReCAPTCHA v2
```python
result = solver.solve_captcha(
    'recaptcha_v2',
    site_key='your_site_key',
    page_url='https://example.com/page'
)
```

#### ReCAPTCHA v3
```python
result = solver.solve_captcha(
    'recaptcha_v3',
    site_key='your_site_key',
    page_url='https://example.com/page',
    action='verify',
    min_score=0.7
)
```

#### hCaptcha
```python
result = solver.solve_captcha(
    'hcaptcha',
    site_key='your_site_key',
    page_url='https://example.com/page'
)
```

## Error Handling

```python
from captcha_solver import CaptchaSolver, CaptchaSolverError

try:
    result = solver.solve_captcha('image', image_path='captcha.png')
except CaptchaSolverError as e:
    print(f'Failed to solve captcha: {e}')
```

## Service-Specific Usage

If you prefer to use a specific service directly:

```python
from captcha_solver import TwoCaptcha, AntiCaptcha, DeathByCaptcha

# Using 2captcha
solver = TwoCaptcha('your_api_key')
result = solver.solve_captcha('image', image_path='captcha.png')

# Using Anti-Captcha
solver = AntiCaptcha('your_api_key')
result = solver.solve_captcha('recaptcha_v2', site_key='key', page_url='url')

# Using DeathByCaptcha
solver = DeathByCaptcha('username:password')
result = solver.solve_captcha('hcaptcha', site_key='key', page_url='url')
```

## Notes

- Make sure to keep your API keys secure and never commit them to version control
- Different services may have different pricing and success rates
- The automatic fallback feature will try all configured services until one succeeds
- Check your account balance regularly to ensure uninterrupted service

## License

MIT License