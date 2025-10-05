"""
Input validation middleware for security
"""

import re
from typing import Any, Dict
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import html


class SecurityValidator:
    """Security validation utilities"""
    
    # Dangerous patterns to block
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # Script tags
        r'javascript:',  # JavaScript protocol
        r'on\w+\s*=',  # Event handlers
        r'<iframe[^>]*>',  # Iframe tags
        r'<object[^>]*>',  # Object tags
        r'<embed[^>]*>',  # Embed tags
        r'<link[^>]*>',  # Link tags
        r'<meta[^>]*>',  # Meta tags
        r'<style[^>]*>.*?</style>',  # Style tags
        r'expression\s*\(',  # CSS expressions
        r'url\s*\(',  # CSS url functions
        r'@import',  # CSS imports
    ]
    
    # SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        r'union\s+select',
        r'drop\s+table',
        r'delete\s+from',
        r'insert\s+into',
        r'update\s+set',
        r'--\s*$',  # SQL comments
        r'/\*.*?\*/',  # SQL block comments
        r';\s*drop',
        r';\s*delete',
        r';\s*insert',
        r';\s*update',
    ]
    
    @classmethod
    def sanitize_string(cls, value: str, max_length: int = 1000) -> str:
        """Sanitize a string input"""
        if not isinstance(value, str):
            return str(value)
        
        # Truncate to max length
        value = value[:max_length]
        
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # HTML encode to prevent XSS
        value = html.escape(value)
        
        return value.strip()
    
    @classmethod
    def validate_input(cls, value: Any, field_name: str = "input") -> Any:
        """Validate and sanitize input"""
        if value is None:
            return value
        
        if isinstance(value, str):
            # Check for dangerous patterns
            for pattern in cls.DANGEROUS_PATTERNS + cls.SQL_INJECTION_PATTERNS:
                if re.search(pattern, value, re.IGNORECASE):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid {field_name}: contains potentially dangerous content"
                    )
            
            # Sanitize the string
            return cls.sanitize_string(value)
        
        elif isinstance(value, dict):
            # Recursively validate dictionary
            return {k: cls.validate_input(v, f"{field_name}.{k}") for k, v in value.items()}
        
        elif isinstance(value, list):
            # Recursively validate list
            return [cls.validate_input(item, f"{field_name}[{i}]") for i, item in enumerate(value)]
        
        return value
    
    @classmethod
    def validate_email(cls, email: str) -> str:
        """Validate email format"""
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is required"
            )
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )
        
        return email.lower().strip()
    
    @classmethod
    def validate_password(cls, password: str) -> str:
        """Validate password strength"""
        if not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password is required"
            )
        
        if len(password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long"
            )
        
        if len(password) > 128:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be less than 128 characters"
            )
        
        # Check for common weak patterns
        weak_patterns = [
            r'password',
            r'123456',
            r'qwerty',
            r'admin',
            r'user',
        ]
        
        for pattern in weak_patterns:
            if re.search(pattern, password, re.IGNORECASE):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Password contains common weak patterns"
                )
        
        return password


async def validate_request_middleware(request: Request, call_next):
    """Middleware to validate incoming requests"""
    try:
        # Basic validation on URL parameters
        for param_name, param_value in request.path_params.items():
            SecurityValidator.validate_input(param_value, f"path_param.{param_name}")
        
        # Basic validation on query parameters
        for param_name, param_value in request.query_params.items():
            SecurityValidator.validate_input(param_value, f"query_param.{param_name}")
        
        # Skip body validation to avoid consuming the request body
        # FastAPI handles JSON parsing automatically
        
        response = await call_next(request)
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log the error and return a generic error response
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error": "Invalid request",
                "message": "Request validation failed"
            }
        )
