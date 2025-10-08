from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from fastapi.templating import Jinja2Templates
from fastapi import status
from fastapi.responses import JSONResponse
from datetime import timedelta

from app.auth.schema import (
    CreateUserModel,
    UserLoginModel,
    TokenModel,
    PasswordResetRequestModel,
    PasswordResetConfirm,
)
from app.config import Config
from app.core.model import User
from app.error import (
    EmailAlreadyExist,
    UsernameAlreadyExist,
    UseNotFound,
    IncorrectEmailOrPassword,
)
from app.utility.security import (
    encode_url_safe_token,
    get_hashed_password,
    decode_url_safe_token,
    verify_password,
    create_access_token,
)
from app.celery_task import send_email

templates = Jinja2Templates(
    directory="app/auth/html_template_mail"
)  # or can use Path from pathlib base_dir


class UserService:

    async def get_user_by_field(
            self, field_check: str, value: str, session: AsyncSession
    ):
        statement = select(User).where(getattr(User, field_check) == value)
        result = await session.exec(statement)
        user = result.first()
        return user

    async def create_user(self, user_data: CreateUserModel, session: AsyncSession):

        user_data_dict = user_data.model_dump(exclude={"password"})
        new_user = User(**user_data_dict)
        new_user.hashed_password = get_hashed_password(user_data.password)
        new_user.role = "user"
        session.add(new_user)
        await session.commit()
        return new_user

    async def update_user(self, user: User, user_data: dict, session: AsyncSession):
        for key, value in user_data.items():
            setattr(user, key, value)
        await session.commit()
        return user

    async def signup_user(self, user_data: CreateUserModel, session: AsyncSession):
        existing_email = await self.get_user_by_field("email", user_data.email, session)
        if existing_email is not None:
            raise EmailAlreadyExist()

        existing_username = await self.get_user_by_field(
            "username", user_data.username, session
        )
        if existing_username:
            raise UsernameAlreadyExist()

        new_user = await self.create_user(user_data, session)

        # Encoding url token
        token = encode_url_safe_token(
            {"email": user_data.email}
        )  # Using URLSafeTimedSerializer encode
        link = f"{Config.DOMAIN_NAME}/{Config.VERSION}/oauth/verify/{token}"
        html_content = templates.get_template("verify_email.html").render(
            {"action_url": link, "first_name": user_data.first_name}
        )

        # Email sending
        emails = [user_data.email]
        subject = "Verification your email"
        send_email.delay(emails, subject, html_content)

        return new_user

    async def verify_user_account(self, token: str, session: AsyncSession):
        token_data = decode_url_safe_token(token)
        user_email = token_data.get("email")
        if user_email:
            user = await self.get_user_by_field("email", user_email, session)
            if not user:
                raise UseNotFound()
            await self.update_user(user, {"is_verified": True}, session)
            return JSONResponse(
                content={"message": "Account verified successfully"},
                status_code=status.HTTP_200_OK,
            )
        return JSONResponse(
            content={"message": "Error occurred during verification"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    async def login_user(self, login_data: UserLoginModel, session: AsyncSession):
        email = login_data.email
        password = login_data.password

        user = await self.get_user_by_field("email", email, session)

        if user is not None:
            password_valid = verify_password(password, user.hashed_password)
            if password_valid:
                access_token = create_access_token(
                    user_data={
                        "email": user.email,
                        "user_id": str(user.id),  # string type is required
                        "role": user.role,
                    },
                    expire_delta=timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES),
                    refresh=False,
                )

                refresh_token = create_access_token(
                    user_data={
                        "email": user.email,
                        "user_id": str(user.id),  # string type is required
                        "role": user.role,
                    },
                    refresh=True,
                    expire_delta=timedelta(days=Config.REFRESH_TOKEN_EXPIRE_DAYS),
                )

                return TokenModel(
                    access_token=access_token, refresh_token=refresh_token
                )

        raise IncorrectEmailOrPassword()

    async def password_reset_request(
            self, email: PasswordResetRequestModel, session: AsyncSession
    ):
        email = email.email
        user = await self.get_user_by_field("email", email, session)
        if user is None:
            raise UseNotFound()
        token = encode_url_safe_token({"email": email})
        link = f"{Config.DOMAIN_NAME}/{Config.VERSION}/password-reset-confirm/{token}"
        html_message = templates.get_template("password-reset.html").render(
            {"action_url": link, "first_name": user.first_name}
        )
        emails = [email]
        subject = "Reset your password"
        send_email.delay(emails, subject, html_message)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Please check your email for instructions to reset your password"
            },
        )

    async def reset_account_password(
            self, token: str, password: PasswordResetConfirm, session: AsyncSession
    ):
        new_password = password.new_password

        token_data = decode_url_safe_token(token)

        user_email = token_data.get("email")

        if user_email:
            user = await self.get_user_by_field("email", user_email, session)
            if not user:
                raise UseNotFound()
            hashed_password = get_hashed_password(new_password)
            await self.update_user(user, {"hashed_password": hashed_password}, session)

            return JSONResponse(
                content={"message": "Password reset successfully"},
                status_code=status.HTTP_200_OK,
            )

        return JSONResponse(
            content={"message": "Error occurred during password reset."},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )