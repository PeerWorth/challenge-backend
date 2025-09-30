from datetime import datetime

from sqlmodel import Field, Relationship, UniqueConstraint

from app.common.mixin.timestamp import TimestampMixin


class UserChallenge(TimestampMixin, table=True):  # type: ignore
    __tablename__: str = "user_challenge"
    __table_args__ = (UniqueConstraint("user_id", "challenge_id"),)

    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False)
    challenge_id: int = Field(foreign_key="challenge.id", nullable=False)
    status: str = Field(default="not_started", nullable=False, description="챌린지 상태")
    mission_step: int = Field(default=1, nullable=False, description="현재 진행 중인 미션 순서")

    missions: list["UserMission"] = Relationship(
        back_populates="user_challenge",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "passive_deletes": True,
        },
    )


class UserMission(TimestampMixin, table=True):  # type: ignore
    __tablename__: str = "user_mission"
    __table_args__ = (UniqueConstraint("user_challenge_id", "mission_id"),)

    id: int = Field(default=None, primary_key=True)
    user_challenge_id: int = Field(foreign_key="user_challenge.id", nullable=False)
    mission_id: int = Field(foreign_key="mission.id", nullable=False)
    post_id: int | None = Field(default=None, foreign_key="post.id", nullable=True, description="미션 수행 포스트")
    status: str = Field(default="not_started", nullable=False, description="미션 상태")
    point: int = Field(default=0, nullable=False, description="획득한 보상 금액")
    completed_at: datetime | None = Field(default=None, nullable=True, description="미션 완료 시간 (UTC)")

    user_challenge: UserChallenge = Relationship(back_populates="missions")
