from sqlmodel import Field, Relationship

from app.common.mixin.timestamp import TimestampMixin


class Challenge(TimestampMixin, table=True):  # type: ignore
    __tablename__: str = "challenge"

    id: int = Field(default=None, primary_key=True)
    title: str = Field(nullable=False, description="챌린지 제목")
    step: int = Field(default=0, nullable=False, description="챌린지 순서")

    missions: list["Mission"] = Relationship(
        back_populates="challenge",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "passive_deletes": True,
            "order_by": "Mission.step",
        },
    )


class Mission(TimestampMixin, table=True):  # type: ignore
    __tablename__: str = "mission"

    id: int = Field(default=None, primary_key=True)
    challenge_id: int = Field(foreign_key="challenge.id", nullable=False)
    title: str = Field(nullable=False, description="미션 제목")
    step: int = Field(default=0, nullable=False, description="미션 순서")
    reward_amount: int = Field(default=0, nullable=False, description="성공 금액 (원)")

    challenge: Challenge = Relationship(back_populates="missions")
