from pydantic import Field

from app.common.schema import CamelBaseModel


class MissionSummary(CamelBaseModel):
    id: int = Field(description="미션 ID")
    title: str = Field(description="미션 제목")
    step: int = Field(description="미션 순서")
    reward_amount: int = Field(description="보상 금액")
    status: str = Field(description="미션 상태")


class ChallengeSummary(CamelBaseModel):
    id: int = Field(description="챌린지 ID")
    title: str = Field(description="챌린지 제목")
    status: str = Field(description="챌린지 상태")
    current_mission_step: int = Field(description="현재 진행 중인 미션 순서")
    missions: list[MissionSummary] = Field(description="미션 목록")


class CurrentChallenge(CamelBaseModel):
    challenge: ChallengeSummary = Field(description="챌린지 정보")
    current_mission: MissionSummary = Field(description="현재 미션 정보")


class CompletedChallenge(CamelBaseModel):
    challenge: ChallengeSummary = Field(description="챌린지 정보")
    total_reward_amount: int = Field(description="총 획득 보상")


class HomePageResponse(CamelBaseModel):
    current_challenge: CurrentChallenge = Field(description="현재 수행 중인 챌린지")
    completed_challenges: list[CompletedChallenge] = Field(description="완료된 챌린지 목록")
