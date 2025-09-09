from enum import StrEnum
from os import getenv


class EnvironmentType(StrEnum):
    DEV = "dev"
    PROD = "prod"

    @property
    def dynamodb_url(self) -> str:
        env_keys = {
            EnvironmentType.DEV: "DEV_DYNAMODB_URL",
            EnvironmentType.PROD: "PROD_DYNAMODB_URL",
        }
        key = env_keys[self]
        url = getenv(key)
        if not url:
            raise ValueError(f"{key} 환경변수가 설정되지 않았습니다.")
        return url
    
    @property
    def db_url(self) -> str:
        env_keys = {
            EnvironmentType.DEV: "DEV_MYSQL_URL",
            EnvironmentType.PROD: "PROD_MYSQL_URL",
        }
        key = env_keys[self]
        url = getenv(key)
        if not url:
            raise ValueError(f"{key} 환경변수가 설정되지 않았습니다.")
        return url

