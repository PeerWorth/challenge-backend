from pydantic import Field

from app.common.schema import CamelBaseModel


class MissionBasic(CamelBaseModel):
    id: int = Field(description="미션 ID")
    title: str = Field(description="미션 제목")
    step: int = Field(description="미션 순서")
    status: str = Field(description="미션 상태")


class MissionSummary(CamelBaseModel):
    id: int = Field(description="미션 ID")
    title: str = Field(description="미션 제목")
    description: str = Field(description="미션 설명")
    step: int = Field(description="미션 순서")
    point: int = Field(description="보상 금액")
    status: str = Field(description="미션 상태")
    type: str = Field(description="미션 타입")
    headcount: int = Field(description="미션 참여 인원")


class ChallengeSummary(CamelBaseModel):
    id: int = Field(description="챌린지 ID")
    title: str = Field(description="챌린지 제목")
    description: str = Field(description="챌린지 설명")
    status: str = Field(description="챌린지 상태")
    missions: list[MissionBasic] = Field(description="미션 목록")
    total_points: int = Field(description="총 금액")


class ChallengeInfoResponse(CamelBaseModel):
    current_mission: MissionSummary | None = Field(description="현재 수행 중인 미션")
    current_challenge: ChallengeSummary | None = Field(description="현재 수행 중인 챌린지")
    completed_challenges: list[ChallengeSummary] | None = Field(description="완료된 챌린지 목록")


class NewChallengeRequest(CamelBaseModel):
    challenge_id: int = Field(description="챌린지 ID")


class NewChallengeResponse(CamelBaseModel):
    status_code: int = Field(description="상태 코드")


class ChallengeDetail(CamelBaseModel):
    id: int = Field(description="챌린지 ID")
    title: str = Field(description="챌린지 제목")
    description: str = Field(description="챌린지 설명")
    total_points: int = Field(description="총 보상 금액")
    status: str = Field(description="유저 챌린지 상태")


class ChallengeListResponse(CamelBaseModel):
    challenges: list[ChallengeDetail] = Field(description="챌린지 목록")


class MissionPost(CamelBaseModel):
    user_id: int = Field(description="유저 ID")
    post_id: int = Field(description="게시물 ID")
    nickname: str = Field(description="닉네임")
    image_url: str | None = Field(description="이미지 URL (Presigned URL)")


class MissionInfoResponse(CamelBaseModel):
    id: int = Field(description="미션 ID")
    title: str = Field(description="미션 제목")
    description: str = Field(description="미션 설명")
    type: str = Field(description="미션 타입")
    point: int = Field(description="보상 포인트")
    headcount: int = Field(description="미션 참여 인원")
    next_cursor: int | None = Field(description="다음 페이지를 위한 커서 (마지막 post_id)")
    posts: list[MissionPost] = Field(description="미션 관련 게시물 목록 (최신 6개)")


class MissionPostsResponse(CamelBaseModel):
    posts: list[MissionPost] = Field(description="미션 관련 게시물 목록")
    next_cursor: int | None = Field(description="다음 페이지를 위한 커서 (마지막 post_id)")
