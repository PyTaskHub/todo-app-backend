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