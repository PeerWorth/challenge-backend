from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, UniqueConstraint

from app.common.mixin.timestamp import TimestampMixin
from app.module.media.enums import UploadType

if TYPE_CHECKING:
    from app.model.user import User


class Post(TimestampMixin, table=True):  # type: ignore
    __tablename__: str = "post"
    __table_args__ = (UniqueConstraint("user_id", "mission_id"),)

    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False)
    mission_id: int = Field(nullable=False)
    content: str = Field(nullable=False)

    image: Optional["PostImage"] = Relationship(
        back_populates="post",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "passive_deletes": True,
            "uselist": False,
        },
    )
    likes: list["PostLike"] = Relationship(
        back_populates="post",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "passive_deletes": True,
        },
    )


class PostImage(TimestampMixin, table=True):  # type: ignore
    __tablename__: str = "post_image"

    id: int = Field(default=None, primary_key=True)
    post_id: int = Field(foreign_key="post.id", nullable=False)
    file_key: str = Field(nullable=False)
    upload_type: UploadType = Field(nullable=False)

    post: Post = Relationship(back_populates="image")


class PostLike(TimestampMixin, table=True):  # type: ignore
    __tablename__: str = "post_like"
    __table_args__ = (UniqueConstraint("user_id", "post_id"),)

    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False, index=True)
    post_id: int = Field(foreign_key="post.id", nullable=False, index=True)

    user: "User" = Relationship()
    post: "Post" = Relationship(back_populates="likes")
