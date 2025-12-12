"""
Pydantic schemas for authentication tokens.
"""

from pydantic import BaseModel, ConfigDict, Field


class Token(BaseModel):
    """
    Access and refresh tokens response.
    Used as a response model for the login endpoint.
    """

    access_token: str = Field(
        description="JWT access token used for authorized requests",
    )
    refresh_token: str = Field(
        description="JWT refresh token used to obtain new access tokens",
    )
    token_type: str = Field(
        default="bearer",
        description='Token type. Always "bearer"',
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.access...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.refresh...",
                "token_type": "bearer",
            }
        }
    )


class TokenData(BaseModel):
    """
    Data extracted from JWT token.
    This describes the structure of JWT tokens used in the project.
    """

    user_id: int | None = Field(
        default=None,
        description="User ID from the database",
    )
    username: str | None = Field(
        default=None,
        description="Username",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": 1,
                "username": "john_doe",
            }
        }
    )


class RefreshTokenRequest(BaseModel):
    """
    Request schema for token refresh.
    """

    refresh_token: str = Field(
        description="Valid JWT refresh token",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.refresh...",
            }
        }
    )


class AccessTokenResponse(BaseModel):
    """
    Response with only access token.
    Used as a response model for the refresh endpoint.
    """

    access_token: str = Field(description="New JWT access token")
    token_type: str = Field(
        default="bearer",
        description='Token type. Always "bearer".',
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.access...",
                "token_type": "bearer",
            }
        }
    )
