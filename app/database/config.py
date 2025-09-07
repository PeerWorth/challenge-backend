from os import getenv

from dotenv import load_dotenv

from app.common.enums import EnvironmentType



load_dotenv()


ENVIRONMENT = getenv("ENVIRONMENT", None)
if not ENVIRONMENT:
    raise ValueError("ENVIRONMENT 환경변수가 설정되지 않았습니다.")

env = EnvironmentType(ENVIRONMENT) 

