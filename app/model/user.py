from datetime import date

from sqlmodel import Field, Relationship, UniqueConstraint

from app.common.mixin.timestamp import TimestampMixin


class User(TimestampMixin, table=True):  # type: ignore
    __tablename__: str = "user"
    __table_args__ = (UniqueConstraint("provider", "social_id"),)

    id: int = Field(default=None, primary_key=True)
    provider: str = Field(nullable=False)
    social_id: str = Field(nullable=False)
    nickname: str = Field(nullable=True, unique=True)
    birthday: date = Field(nullable=True)
    gender: bool = Field(nullable=True)
    phone: str = Field(nullable=True)

    consent: list["UserConsent"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "passive_deletes": True,
        },
    )


class UserConsent(TimestampMixin, table=True):  # type: ignore
    __tablename__: str = "user_consent"

    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False)
    event: str = Field(description="동의사항")
    agree: bool = Field(description="동의여부")

    user: User = Relationship(back_populates="consent")
