from pydantic import BaseModel, ConfigDict
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
