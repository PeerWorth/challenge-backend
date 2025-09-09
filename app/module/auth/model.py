from datetime import date

from sqlmodel import Field, Relationship

from app.common.mixin.timestamp import TimestampMixin


class User(TimestampMixin, table=True):  # type: ignore
    __tablename__: str = "user"

    id: int = Field(default=None, primary_key=True)
    social_id: str = Field(nullable=False, unique=True)
    nickname: str = Field(nullable=True, unique=True)
    birthday: date
    gender: bool
    phone: str

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
