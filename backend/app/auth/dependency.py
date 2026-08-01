import jwt
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated, Any
from fastapi import Depends, HTTPException, status
from passlib.exc import InvalidTokenError

from app.core.dependency import SessionDep
from app.config import Config
from app.core.redis import token_in_blocklist
from app.auth.services import UserService
from app.core.model import User


user_service = UserService()
oauth_scheme = OAuth2PasswordBearer(tokenUrl="login")


class TokenBearer:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    async def __call__(self, token: Annotated[str, Depends(oauth_scheme)]):
        try:
            payload = jwt.decode(
                token, Config.SECRET_KEY, algorithms=[Config.ALGORITHM]
            )
            jti = payload.get("jti")

            if jti is None or await token_in_blocklist(jti):
                raise self.credentials_exception

            self.verify_token_data(payload)
            return payload

        except InvalidTokenError:
            raise self.credentials_exception
        except jwt.exceptions.PyJWTError:
            raise self.credentials_exception

    def verify_token_data(self, payload: dict) -> None:
        pass


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, payload: dict) -> None:
        if payload.get("refresh"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access token is required",
                headers={"WWW-Authenticate": "Bearer"},
            )


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, payload: dict) -> None:
        if not payload.get("refresh"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token is required",
                headers={"WWW-Authenticate": "Bearer"},
            )


async def get_current_user(
    token_details: Annotated[dict, Depends(AccessTokenBearer())], session: SessionDep
):
    user_email = token_details["user"]["email"]
    user = await user_service.get_user_by_field("email", user_email, session)
    return user


class RoleChecker:
    def __init__(self, allowed_roles: list[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: Annotated[User, Depends(get_current_user)]) -> Any:
        if not current_user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "message": "Account not verified",
                    "hint": "Please check your email for verification details",
                },
            )
        if current_user.role in self.allowed_roles:
            return True
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "message": "You dont not have enough permissions to perform this action",
                "error_code": "insufficient_permission",
            },
        )
