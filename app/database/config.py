from os import getenv

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.common.enums import EnvironmentType
from app.database.constant import CONNECTION_TIMEOUT_SECOND, DB_MAX_OVERFLOW, DB_POOL_SIZE, POOL_TIMEOUT_SECOND

load_dotenv()


ENVIRONMENT = getenv("ENVIRONMENT", None)
if not ENVIRONMENT:
    raise ValueError("ENVIRONMENT 환경변수가 설정되지 않았습니다.")

try:
    env = EnvironmentType(ENVIRONMENT)  # type: ignore[arg-type]
except ValueError:
    raise ValueError(f"정의되지 않는 환경 변수 값입니다. {ENVIRONMENT=}")

MYSQL_URL = env.db_url

mysql_engine = create_async_engine(
    MYSQL_URL,
    pool_pre_ping=True,
    pool_size=DB_POOL_SIZE,
    max_overflow=DB_MAX_OVERFLOW,
    pool_timeout=POOL_TIMEOUT_SECOND,
    connect_args={"connect_timeout": CONNECTION_TIMEOUT_SECOND},
)


mysql_session_factory = async_sessionmaker(bind=mysql_engine, class_=AsyncSession, expire_on_commit=False)
