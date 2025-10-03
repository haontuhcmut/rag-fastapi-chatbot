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

class InvalidIDFormat(ExceptionRegister):
    """Invalid ID format"""

    pass

class FileNotFound(ExceptionRegister):
    """File not found"""

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


    app.add_exception_handler(
        CategoryNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Category not found",
                "error_code": "category_not_found",
            },
        ),
    )

    app.add_exception_handler(
        InvalidIDFormat,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Invalid ID format", "error_code": "invalid_id_format"},
        ),
    )

    app.add_exception_handler(
        CategoryAlreadyExist,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Category name already exist",
                "error_code": "category_name_already_exist",
            },
        ),
    )

    app.add_exception_handler(
        PTSChemeNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "PT scheme not found",
                "error_code": "pt_scheme_not_found",
            },
        ),
    )

    app.add_exception_handler(
        PTSchemeAlreadyExist,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "PT scheme code already exist",
                "error_code": "pt_scheme_code_already_exist",
            },
        ),
    )

    app.add_exception_handler(
        ProductNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Product not found", "error_code": "product_not_found"},
        ),
    )

    app.add_exception_handler(
        ProductAlreadyExist,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Product already exist",
                "error_code": "product_already_exist",
            },
        ),
    )

    app.add_exception_handler(
        BomNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Bill of material not found",
                "error_code": "bom_not_found",
            },
        ),
    )

    app.add_exception_handler(
        MaterialNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Material not found",
                "error_code": "material_not_found",
            },
        ),
    )

    app.add_exception_handler(
        MaterialAlreadyExist,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Material already exist",
                "error_code": "material_already_code",
            },
        ),
    )

    app.add_exception_handler(
        WarehouseNotFound,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Warehouse not found",
                "error_code": "warehouse_not_found",
            },
        ),
    )

    app.add_exception_handler(
        InvalidFileExtension,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Invalid file extension",
                "error_code": "invalid_file_extension",
            },
        ),
    )

    app.add_exception_handler(
        FileNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "File not found",
                "error_code": "file_not_found",
            },
        ),
    )