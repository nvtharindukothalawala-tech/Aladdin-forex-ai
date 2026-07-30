"""
auth_schema.py

Schemas for authentication APIs.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from pydantic import BaseModel


class UserRegisterRequest(BaseModel):
    """
    User registration request.
    """

    username: str

    email: str

    password: str


class UserLoginRequest(BaseModel):
    """
    User login request.
    """

    username: str

    password: str


class TokenResponse(BaseModel):
    """
    JWT token response.
    """

    access_token: str

    token_type: str
