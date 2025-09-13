from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from mangum import Mangum
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.auth.v1.router import auth_router
from app.api.user.v1.router import user_router
from app.common.exception_handlers import (
    auth_exception_handler,
    general_exception_handler,
    http_exception_handler,
    pydantic_validation_exception_handler,
    starlette_http_exception_handler,
    validation_exception_handler,
)
from app.module.auth.error import AuthException

app = FastAPI()

app.add_exception_handler(AuthException, auth_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(StarletteHTTPException, starlette_http_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(ValidationError, pydantic_validation_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(Exception, general_exception_handler)

app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(user_router, prefix="/api/user", tags=["user"])


@app.get("/health")
def health():
    return {"status": "ok"}


handler = Mangum(app)
