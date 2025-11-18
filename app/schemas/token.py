"""
Pydantic schemas for authentication tokens.
"""
from pydantic import BaseModel


class Token(BaseModel):
    """
    Access and refresh tokens response.
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """
    Data extracted from JWT token.
    """
    user_id: int | None = None
    username: str | None = None


class RefreshTokenRequest(BaseModel):
    """
    Request schema for token refresh.
    """
    refresh_token: str


class AccessTokenResponse(BaseModel):
    """
    Response with only access token.
    """
    access_token: str
    token_type: str = "bearer"