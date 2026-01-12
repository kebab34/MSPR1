"""
Authentication utilities using Supabase Auth
"""
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional, Dict, Any
from app.core.config import settings
from app.core.database import supabase


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify JWT token using Supabase JWT secret
    
    Args:
        token: JWT token to verify
        
    Returns:
        Decoded token payload if valid, None otherwise
    """
    try:
        # Verify token using Supabase JWT secret
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_signature": True}
        )
        return payload
    except JWTError:
        return None


def get_user_from_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Get user information from Supabase token
    
    Args:
        token: JWT token from Supabase Auth
        
    Returns:
        User information if token is valid, None otherwise
    """
    try:
        # Verify token first
        payload = verify_token(token)
        if not payload:
            return None
        
        # Supabase tokens contain user information in the payload
        # Extract user info from the token payload
        user_id = payload.get("sub")  # Subject (user ID)
        email = payload.get("email")
        user_metadata = payload.get("user_metadata", {})
        app_metadata = payload.get("app_metadata", {})
        
        if not user_id:
            return None
        
        return {
            "id": user_id,
            "email": email,
            "user_metadata": user_metadata,
            "app_metadata": app_metadata,
            "aud": payload.get("aud"),  # Audience
            "role": payload.get("role")  # User role
        }
    except Exception:
        return None


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Create JWT access token using Supabase JWT secret
    
    Note: For user authentication, prefer using Supabase Auth
    which handles token creation automatically.
    This function is kept for backward compatibility.
    
    Args:
        data: Data to encode in the token
        expires_delta: Optional expiration time delta
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(seconds=settings.JWT_EXPIRATION)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def sign_in_with_email(email: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Sign in user with email and password using Supabase Auth
    
    Args:
        email: User email
        password: User password
        
    Returns:
        Session data with access_token and user info, None if failed
    """
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "user": response.user.dict() if response.user else None
        }
    except Exception:
        return None


def sign_up_with_email(email: str, password: str, metadata: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
    """
    Sign up new user with email and password using Supabase Auth
    
    Args:
        email: User email
        password: User password
        metadata: Optional user metadata
        
    Returns:
        Session data with access_token and user info, None if failed
    """
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": metadata or {}
            }
        })
        if response.session:
            return {
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token,
                "user": response.user.dict() if response.user else None
            }
        return {
            "user": response.user.dict() if response.user else None
        }
    except Exception:
        return None


