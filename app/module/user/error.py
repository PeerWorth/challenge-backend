from fastapi import status


class UserException(Exception):
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail: str = "사용자 관련 서버 오류"

    def __init__(self, detail: str | None = None):
        self.detail = detail or self.detail


class UserNotFoundException(UserException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "사용자를 찾을 수 없습니다."
