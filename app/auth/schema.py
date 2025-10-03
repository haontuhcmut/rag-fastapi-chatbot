from pydantic_core.core_schema import FieldValidationInfo
from pydantic import BaseModel, Field, field_validator
import re


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

    @field_validator("confirm_password")
    def passwords_match(cls, v, info: FieldValidationInfo):
        if 'password' in info.data and v != info.data['password']:
            raise ValueError("Passwords do not match.")
        return v


class UserLoginModel(BaseModel):
    email: str = Field(max_length=32)
    password: str = Field(max_length=32)


class AccessTokenModel(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenModel(AccessTokenModel):
    refresh_token: str


class UserModel(BaseModel):
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

    @field_validator("confirm_new_password")
    def passwords_match(cls, v, info: FieldValidationInfo):
        if 'password' in info.data and v != info.data['password']:
            raise ValueError("Passwords do not match.")
        return v