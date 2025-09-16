from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from mangum import Mangum
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.auth.v1.router import auth_router
from app.api.media.v1.router import media_router
from app.api.post.v1.router import post_router
from app.api.user.v1.router import user_router
from app.common.exception_handlers import (
    custom_exception_handler,
    general_exception_handler,
    http_exception_handler,
    pydantic_validation_exception_handler,
    starlette_http_exception_handler,
    validation_exception_handler,
)
from app.module.auth.error import AuthException
from app.module.user.error import UserException

app = FastAPI()

app.add_exception_handler(AuthException, custom_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(UserException, custom_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(StarletteHTTPException, starlette_http_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(ValidationError, pydantic_validation_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(Exception, general_exception_handler)

app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(user_router, prefix="/api/user", tags=["user"])
app.include_router(media_router, prefix="/api/media", tags=["media"])
app.include_router(post_router, prefix="/api/post", tags=["post"])


@app.get("/health")
def health():
    return {"status": "ok"}


handler = Mangum(app)
