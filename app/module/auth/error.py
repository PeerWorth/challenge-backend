from fastapi import status


class AuthException(Exception):
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail: str = "서버 오류"

    def __init__(self, detail: str | None = None):
        self.detail = detail or self.detail


class NoKakaoURLException(AuthException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "카카오 api URL이 존재하지 않습니다.."


class InvalidKakaoTokenException(AuthException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "유효하지 않은 Kakao ID Token입니다."


class MissingSocialIDException(AuthException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "ID Token에 유저 ID가 없습니다."


class NoJWTSecretException(AuthException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "ID Token에 유저 ID가 없습니다."
