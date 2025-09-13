from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class CamelBaseModel(BaseModel):
    """
    camelCase와 snake_case 간 자동 변환을 지원하는 BaseModel.

    - 입력: 클라이언트로부터 camelCase 형식 허용
    - 출력: 클라이언트에게 camelCase 형식으로 반환
    - 내부: Python 코드에서는 snake_case 사용
    """

    model_config = ConfigDict(
        alias_generator=to_camel,  # snake_case를 camelCase로 변환
        populate_by_name=True,  # camelCase와 snake_case 입력 모두 허용
        from_attributes=True,  # ORM 모델로부터 생성 가능
    )


class ErrorDetail(CamelBaseModel):
    type: str = Field(default=..., description="에러 타입", examples=["ValidationError"])
    details: dict[str, Any] | None = Field(
        default=None, description="에러 상세 필드별 메시지", examples=[{"email": "이메일 형식이 잘못되었습니다."}]
    )


class ErrorResponse(CamelBaseModel):
    code: int = Field(default=..., description="HTTP 상태 코드", examples=[403])
    message: str = Field(default=..., description="에러 메시지", examples=["유효하지 않은 요청입니다."])
    error: ErrorDetail
    success: bool = Field(default=False, description="성공 여부", examples=[False])
