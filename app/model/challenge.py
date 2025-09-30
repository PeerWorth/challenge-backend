from sqlmodel import Field, Relationship

from app.common.mixin.timestamp import TimestampMixin


class ChallengeMission(TimestampMixin, table=True):  # type: ignore
    __tablename__: str = "challenge_mission"

    id: int = Field(default=None, primary_key=True)
    challenge_id: int = Field(foreign_key="challenge.id", nullable=False)
    mission_id: int = Field(foreign_key="mission.id", nullable=False)
    step: int = Field(default=1, nullable=False, description="챌린지 내 미션 순서")


class Challenge(TimestampMixin, table=True):  # type: ignore
    __tablename__: str = "challenge"

    id: int = Field(default=None, primary_key=True)
    title: str = Field(nullable=False, description="챌린지 제목")
    description: str = Field(nullable=False, description="챌린지 설명")
    goal: int = Field(default=1, nullable=False, description="챌린지 성공을 위한 최소 미션 완료 개수")

    missions: list["Mission"] = Relationship(
        back_populates="challenges",
        link_model=ChallengeMission,
        sa_relationship_kwargs={
            "order_by": "ChallengeMission.step",
        },
    )


class Mission(TimestampMixin, table=True):  # type: ignore
    __tablename__: str = "mission"

    id: int = Field(default=None, primary_key=True)
    title: str = Field(nullable=False, description="미션 제목")
    description: str = Field(nullable=False, description="미션 설명")
    type: str = Field(nullable=False, description="미션 타입")
    point: int = Field(default=0, nullable=False, description="성공 포인트")

    challenges: list["Challenge"] = Relationship(
        back_populates="missions",
        link_model=ChallengeMission,
        sa_relationship_kwargs={
            "order_by": "ChallengeMission.step",
        },
    )
