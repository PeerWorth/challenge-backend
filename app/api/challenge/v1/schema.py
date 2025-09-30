from pydantic import Field

from app.common.schema import CamelBaseModel


class MissionSummary(CamelBaseModel):
    id: int = Field(description="미션 ID")
    title: str = Field(description="미션 제목")
    description: str = Field(description="미션 설명")
    step: int = Field(description="미션 순서")
    point: int = Field(description="보상 금액")
    status: str = Field(description="미션 상태")
    participant: int | None = Field(description="참여 인원")


class ChallengeSummary(CamelBaseModel):
    id: int = Field(description="챌린지 ID")
    title: str = Field(description="챌린지 제목")
    description: str = Field(description="챌린지 설명")
    status: str = Field(description="챌린지 상태")
    current_mission_step: int | None = Field(description="현재 진행 중인 미션 순서")
    missions: list[MissionSummary] = Field(description="미션 목록")
    total_points: int = Field(description="총 금액")


class ChallengeInfoResponse(CamelBaseModel):
    current_challenge: ChallengeSummary | None = Field(description="현재 수행 중인 챌린지")
    completed_challenges: list[ChallengeSummary] | None = Field(description="완료된 챌린지 목록")


class NewChallengeRequest(CamelBaseModel):
    challenge_id: int = Field(description="챌린지 ID")


class NewChallengeResponse(CamelBaseModel):
    status_code: int = Field(description="상태 코드")
