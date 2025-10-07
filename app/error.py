from typing import Any, Callable
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi import FastAPI, status


class ExceptionRegister(Exception):
    """This is the base class for all exceptions"""

    pass

class EmailAlreadyExist(ExceptionRegister):
    """Email already exist"""

    pass

class IncorrectEmailOrPassword(ExceptionRegister):
    """User has provided wrong email or password during login"""

    pass

class UsernameAlreadyExist(ExceptionRegister):
    """Username already exist"""

    pass

class UseNotFound(ExceptionRegister):
    """User not found"""

    pass

def create_exception_handler(
    status_code: int, detail: Any
) -> Callable[[Request, Exception], JSONResponse]:
    async def exception_handler(requests: Request, exc: ExceptionRegister):
        return JSONResponse(content=detail, status_code=status_code)

    return exception_handler


def register_all_errors(app: FastAPI):
    app.add_exception_handler(
        EmailAlreadyExist,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Email already exist",
                "error_code": "email_already_exist"
            }
        )
    )

    app.add_exception_handler(
        IncorrectEmailOrPassword,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "message": "Incorrect email or password",
                "error_code": "incorrect_email_or_password"
            }
        )


    )

    app.add_exception_handler(
        UseNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "User not found",
                "error_code": "user_not_found"
            }
        )
    )

    app.add_exception_handler(
        UsernameAlreadyExist,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Username already exist",
                "error_code": "username_already_exist"
            }
        )
    )