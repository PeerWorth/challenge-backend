from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, UniqueConstraint

from app.common.mixin.timestamp import TimestampMixin

if TYPE_CHECKING:
    from app.model.user import User


class Badge(TimestampMixin, table=True):  # type: ignore
    __tablename__: str = "badge"

    id: int = Field(default=None, primary_key=True)
    category: str = Field(nullable=False)
    name: str = Field(nullable=False)
    description: str = Field(nullable=False)

    user_badges: list["UserBadge"] = Relationship(
        back_populates="badge",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "passive_deletes": True,
        },
    )


class UserBadge(TimestampMixin, table=True):  # type: ignore
    __tablename__: str = "user_badge"
    __table_args__ = (UniqueConstraint("user_id", "badge_id"),)

    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False, index=True)
    badge_id: int = Field(foreign_key="badge.id", nullable=False, index=True)

    user: "User" = Relationship(back_populates="user_badges")
    badge: "Badge" = Relationship(back_populates="user_badges")
