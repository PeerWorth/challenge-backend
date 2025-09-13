from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.common.schema import ErrorDetail, ErrorResponse


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    error_response = ErrorResponse(
        code=exc.status_code,
        message=exc.detail if isinstance(exc.detail, str) else "에러가 발생했습니다.",
        error=ErrorDetail(type="HTTPException", details=exc.detail if isinstance(exc.detail, dict) else None),
        success=False,
    )

    return JSONResponse(status_code=exc.status_code, content=error_response.model_dump(by_alias=True))


async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    error_response = ErrorResponse(
        code=exc.status_code,
        message=exc.detail if isinstance(exc.detail, str) else "에러가 발생했습니다.",
        error=ErrorDetail(type="HTTPException", details=exc.detail if isinstance(exc.detail, dict) else None),
        success=False,
    )

    return JSONResponse(status_code=exc.status_code, content=error_response.model_dump(by_alias=True))


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors_dict = {}
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"][1:])  # body 제거
        if field:
            errors_dict[field] = error["msg"]

    error_response = ErrorResponse(
        code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="입력값 검증에 실패했습니다.",
        error=ErrorDetail(
            type="ValidationError", details=errors_dict if errors_dict else {"general": "입력값을 확인해주세요."}
        ),
        success=False,
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=error_response.model_dump(by_alias=True)
    )


async def pydantic_validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    errors_dict = {}
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors_dict[field] = error["msg"]

    error_response = ErrorResponse(
        code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="데이터 검증에 실패했습니다.",
        error=ErrorDetail(type="ValidationError", details=errors_dict),
        success=False,
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=error_response.model_dump(by_alias=True)
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    error_response = ErrorResponse(
        code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="서버 내부 오류가 발생했습니다.",
        error=ErrorDetail(type="InternalServerError", details=None),
        success=False,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=error_response.model_dump(by_alias=True)
    )
