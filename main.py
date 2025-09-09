from fastapi import FastAPI
from mangum import Mangum

from app.api.auth.v1.router import auth_router

app = FastAPI()

app.include_router(auth_router, prefix="/api/auth", tags=["auth"])


@app.get("/health")
def health():
    return {"status": "ok"}


handler = Mangum(app)
