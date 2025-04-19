from pydantic import BaseModel

# 🔐 Token schema used for access and refresh responses
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

# 🌐 Refresh token input schema
class RefreshToken(BaseModel):
    refresh_token: str
