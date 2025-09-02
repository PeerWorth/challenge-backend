from os import getenv
from typing import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.enums import EnvironmentType
from database.config import mysql_session_factory

load_dotenv()

ENVIRONMENT = getenv("ENVIRONMENT", None)
if not ENVIRONMENT:
    raise ValueError("ENVIRONMENT 환경변수가 설정되지 않았습니다.")
try:
    env = EnvironmentType(ENVIRONMENT)  # type: ignore[arg-type]
except ValueError:
    raise ValueError(f"정의되지 않는 환경 변수 값입니다. {ENVIRONMENT=}")



async def get_mysql_session_router() -> AsyncGenerator[AsyncSession, None]:
    session = mysql_session_factory()
    try:
        yield session
    finally:
        await session.close()

