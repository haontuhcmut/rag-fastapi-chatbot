from pydantic_core.core_schema import FieldValidationInfo
from pydantic import BaseModel, Field, field_validator, model_validator
import re
from datetime import datetime
from uuid import UUID


class CreateUserModel(BaseModel):
    email: str
    username: str = Field(max_length=32)
    last_name: str = Field(max_length=32)
    first_name: str = Field(max_length=32)
    password: str = Field(max_length=64)
    confirm_password: str

    @field_validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters.")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", v):
            raise ValueError("Must contain at least one lowercase letter.")
        if not re.search(r"\d", v):
            raise ValueError("Must contain at least one digit.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Must contain at least one special character.")
        return v

    @model_validator(mode="after")
    def check_passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match.")
        return self


class UserLoginModel(BaseModel):
    email: str = Field(max_length=32)
    password: str = Field(max_length=32)


class AccessTokenModel(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenModel(AccessTokenModel):
    refresh_token: str


class UserModel(BaseModel):
    id: UUID
    username: str
    last_name: str
    first_name: str
    role: str


class PasswordResetRequestModel(BaseModel):
    email: str


class PasswordResetConfirm(BaseModel):
    new_password: str = Field(max_length=64)
    confirm_new_password: str = Field(max_length=64)

    @field_validator("new_password")
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters.")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", v):
            raise ValueError("Must contain at least one lowercase letter.")
        if not re.search(r"\d", v):
            raise ValueError("Must contain at least one digit.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Must contain at least one special character.")
        return v

    @model_validator(mode="after")
    def check_passwords_match(self):
        if self.new_password != self.confirm_new_password:
            raise ValueError("Passwords do not match.")
        return self


class APIKeyBase(BaseModel):
    name: str
    is_active: bool = True


class APIKeyCreate(APIKeyBase):
    pass


class APIKeyUpdate(BaseModel):
    name: str | None = None
    is_active: bool | None = None


class APIKeyLastUserUpdate(BaseModel):
    last_user_at: datetime


class APIKeyResponse(APIKeyBase):
    id: UUID
    key: str
    user_id: UUID
    last_used_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
