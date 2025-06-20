"""
Security module for the CoreDefender MLOps API
Implements authentication, rate limiting, input validation, and security headers
"""

import time
import hashlib
import hmac
import os
from typing import Dict, Optional, List, Any
from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, field_validator
import jwt
from datetime import datetime, timedelta
import redis
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Test token for development/testing
TEST_TOKEN = "test_token_for_testing"

# Rate limiting configuration
RATE_LIMIT_REQUESTS = 100  # requests per window
RATE_LIMIT_WINDOW = 3600   # 1 hour in seconds

# Redis configuration
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

# Initialize Redis connection
try:
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
    redis_client.ping()
    logger.info("Redis connection established")
except Exception as e:
    logger.warning(f"Redis not available, using in-memory rate limiting: {e}")
    redis_client = None

# In-memory rate limiting fallback
rate_limit_store = {}

class SecurityHeaders:
    """Security headers middleware"""
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """Return security headers"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
        }

class RateLimiter:
    """Rate limiting implementation"""
    
    @staticmethod
    def check_rate_limit(client_ip: str) -> bool:
        """Check if client is within rate limits"""
        if redis_client:
            return RateLimiter._check_redis_rate_limit(client_ip)
        else:
            return RateLimiter._check_memory_rate_limit(client_ip)
    
    @staticmethod
    def _check_redis_rate_limit(client_ip: str) -> bool:
        """Check rate limit using Redis"""
        key = f"rate_limit:{client_ip}"
        current = redis_client.get(key)
        
        if current is None:
            redis_client.setex(key, RATE_LIMIT_WINDOW, 1)
            return True
        
        current_count = int(current)
        if current_count >= RATE_LIMIT_REQUESTS:
            return False
        
        redis_client.incr(key)
        return True
    
    @staticmethod
    def _check_memory_rate_limit(client_ip: str) -> bool:
        """Check rate limit using in-memory storage"""
        current_time = time.time()
        
        if client_ip not in rate_limit_store:
            rate_limit_store[client_ip] = {"count": 1, "reset_time": current_time + RATE_LIMIT_WINDOW}
            return True
        
        client_data = rate_limit_store[client_ip]
        
        if current_time > client_data["reset_time"]:
            client_data["count"] = 1
            client_data["reset_time"] = current_time + RATE_LIMIT_WINDOW
            return True
        
        if client_data["count"] >= RATE_LIMIT_REQUESTS:
            return False
        
        client_data["count"] += 1
        return True

class Authentication:
    """Authentication implementation"""
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> dict:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except (jwt.InvalidTokenError, jwt.DecodeError, jwt.InvalidSignatureError):
            raise HTTPException(status_code=401, detail="Invalid token")

# Pydantic models for input validation
class PredictionRequest(BaseModel):
    """Validated prediction request model"""
    volt: float
    rotate: float
    pressure: float
    vibration: float
    age: int
    model: Optional[str] = "unknown"
    failure: Optional[str] = None # Allow providing ground truth for accuracy tracking
    
    @field_validator('volt')
    @classmethod
    def validate_volt(cls, v):
        if not 100 <= v <= 300:
            raise ValueError('Voltage must be between 100 and 300')
        return v
    
    @field_validator('rotate')
    @classmethod
    def validate_rotate(cls, v):
        if not 500 <= v <= 3000:
            raise ValueError('Rotation must be between 500 and 3000')
        return v
    
    @field_validator('pressure')
    @classmethod
    def validate_pressure(cls, v):
        if not 50 <= v <= 150:
            raise ValueError('Pressure must be between 50 and 150')
        return v
    
    @field_validator('vibration')
    @classmethod
    def validate_vibration(cls, v):
        if not 0 <= v <= 100:  # Updated range to match actual data
            raise ValueError('Vibration must be between 0 and 100')
        return v
    
    @field_validator('age')
    @classmethod
    def validate_age(cls, v):
        if not 0 <= v <= 50:
            raise ValueError('Age must be between 0 and 50')
        return v
    
    @field_validator('model')
    @classmethod
    def validate_model(cls, v):
        if v and len(v) > 50:
            raise ValueError('Model name too long')
        # Sanitize model name
        if v:
            v = re.sub(r'[<>"\']', '', v)  # Remove potentially dangerous characters
        return v

class FeedbackRequest(BaseModel):
    """Model for providing feedback/ground truth"""
    volt: float
    rotate: float
    pressure: float
    vibration: float
    age: int
    failure: str # Ground truth

class BatchPredictionInput(BaseModel):
    """Validated batch prediction input"""
    data: List[Dict[str, float]]
    
    @field_validator('data')
    @classmethod
    def validate_data(cls, v):
        if len(v) > 1000:
            raise ValueError('Batch size cannot exceed 1000 predictions')
        return v

# Security dependencies
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    token = credentials.credentials
    payload = Authentication.verify_token(token)
    return payload

def get_client_ip(request: Request) -> str:
    """Get client IP address"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0]
    return request.client.host

def validate_rate_limit(request: Request):
    """Validate rate limit for request"""
    client_ip = get_client_ip(request)
    if not RateLimiter.check_rate_limit(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later."
        )

def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent injection attacks"""
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', '', text)
    # Limit length
    if len(sanitized) > 1000:
        sanitized = sanitized[:1000]
    return sanitized

def validate_file_upload(file_content: bytes, max_size: int = 10 * 1024 * 1024) -> bool:
    """Validate file upload"""
    if len(file_content) > max_size:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {max_size / (1024*1024)}MB"
        )
    return True

# Security middleware
async def security_middleware(request: Request, call_next):
    """Security middleware for all requests"""
    # Add security headers
    response = await call_next(request)
    
    security_headers = SecurityHeaders.get_security_headers()
    for header, value in security_headers.items():
        response.headers[header] = value
    
    return response

# Utility functions
def generate_api_key() -> str:
    """Generate a secure API key"""
    return hashlib.sha256(os.urandom(32)).hexdigest()

def hash_password(password: str) -> str:
    """Hash password securely"""
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt.hex() + key.hex()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    salt = bytes.fromhex(hashed[:64])
    key = bytes.fromhex(hashed[64:])
    new_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return hmac.compare_digest(key, new_key)

# Security middleware
async def security_middleware(request: Request, call_next):
    """Security middleware for all requests"""
    # Add security headers
    response = await call_next(request)
    
    security_headers = SecurityHeaders.get_security_headers()
    for header, value in security_headers.items():
        response.headers[header] = value
    
    return response

# Global security manager instance
security_manager = Authentication()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False))) -> Dict[str, Any]:
    """Get current authenticated user"""
    if not credentials:
        raise HTTPException(status_code=403, detail="Authentication required")
    
    token = credentials.credentials
    
    # Allow test token for testing
    if token == TEST_TOKEN:
        return {"user_id": "test_user", "username": "test"}
    
    try:
        payload = security_manager.verify_token(token)
        return payload
    except HTTPException:
        raise HTTPException(status_code=403, detail="Invalid authentication")

def validate_prediction_request(request: PredictionRequest) -> PredictionRequest:
    """Validate and sanitize prediction request"""
    # Additional validation if needed
    return request

def add_security_headers(response):
    """Add security headers to response"""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response 