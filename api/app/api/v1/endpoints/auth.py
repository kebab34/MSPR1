"""
Authentication endpoints using Supabase Auth
"""
from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional
from pydantic import BaseModel, EmailStr
from app.utils.auth import (
    verify_token,
    get_user_from_token,
    sign_in_with_email,
    sign_up_with_email
)

router = APIRouter()


class SignInRequest(BaseModel):
    """Sign in request model"""
    email: EmailStr
    password: str


class SignUpRequest(BaseModel):
    """Sign up request model"""
    email: EmailStr
    password: str
    metadata: Optional[dict] = None


class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    refresh_token: Optional[str] = None
    user: Optional[dict] = None


@router.post("/sign-in", response_model=TokenResponse)
async def sign_in(request: SignInRequest):
    """
    Sign in user with email and password
    
    Returns JWT token from Supabase Auth
    """
    result = sign_in_with_email(request.email, request.password)
    if not result:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    return TokenResponse(**result)


@router.post("/sign-up", response_model=TokenResponse)
async def sign_up(request: SignUpRequest):
    """
    Sign up new user with email and password
    
    Returns JWT token from Supabase Auth
    """
    result = sign_up_with_email(
        request.email,
        request.password,
        request.metadata
    )
    if not result:
        raise HTTPException(
            status_code=400,
            detail="Failed to create user"
        )
    return TokenResponse(**result)


@router.get("/me")
async def get_current_user(authorization: Optional[str] = Header(None)):
    """
    Get current user from JWT token
    
    Requires Authorization header: Bearer <token>
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing"
        )
    
    # Extract token from "Bearer <token>"
    try:
        token = authorization.split(" ")[1]
    except IndexError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format"
        )
    
    # Verify token and get user
    user = get_user_from_token(token)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )
    
    return {"user": user}


@router.get("/verify")
async def verify_jwt_token(authorization: Optional[str] = Header(None)):
    """
    Verify JWT token validity
    
    Requires Authorization header: Bearer <token>
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing"
        )
    
    try:
        token = authorization.split(" ")[1]
    except IndexError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format"
        )
    
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )
    
    return {"valid": True, "payload": payload}

