import sys
from pathlib import Path
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import create_engine
from alembic import context

sys.path.append(str(Path(__file__).parent.parent))

from app.common.enums import EnvironmentType
from app.module.auth.model import User, UserConsent  # noqa: F401
from sqlmodel import SQLModel

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata


def get_url() -> str:
    from dotenv import load_dotenv
    from os import getenv
    
    load_dotenv()
    environment = getenv("ENVIRONMENT", "dev")
    env = EnvironmentType(environment)
    
    db_url = env.db_url
    if db_url.startswith("aiomysql"):
        db_url = db_url.replace("aiomysql", "pymysql")
    elif "+aiomysql" in db_url:
        db_url = db_url.replace("+aiomysql", "+pymysql")
    
    return db_url


def run_migrations_online() -> None:
    url = get_url()
    connectable = create_engine(url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
