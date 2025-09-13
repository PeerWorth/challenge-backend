from os import getenv

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from app.common.enums import EnvironmentType
from app.database.constant import MAX_OVERFLOW, POOL_RECYCLE, POOL_SIZE

load_dotenv()

ENVIRONMENT = getenv("ENVIRONMENT", None)
if not ENVIRONMENT:
    raise ValueError("ENVIRONMENT 환경변수가 설정되지 않았습니다.")

env = EnvironmentType(ENVIRONMENT)

engine: AsyncEngine | None = None
async_session_maker: async_sessionmaker | None = None


def get_database_engine() -> AsyncEngine:
    global engine
    if engine is None:
        database_url = env.db_url

        engine = create_async_engine(
            database_url,
            pool_size=POOL_SIZE,
            max_overflow=MAX_OVERFLOW,
            pool_pre_ping=True,
            pool_recycle=POOL_RECYCLE,
            echo=False,
        )
    return engine


def get_async_session_maker() -> async_sessionmaker:
    global async_session_maker
    if async_session_maker is None:
        engine = get_database_engine()
        async_session_maker = async_sessionmaker(
            engine,
            expire_on_commit=False,
        )
    return async_session_maker
