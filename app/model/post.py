from typing import Optional

from sqlmodel import Field, Relationship, UniqueConstraint

from app.common.mixin.timestamp import TimestampMixin
from app.module.media.enums import UploadType


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


class PostImage(TimestampMixin, table=True):  # type: ignore
    __tablename__: str = "post_image"

    id: int = Field(default=None, primary_key=True)
    post_id: int = Field(foreign_key="post.id", nullable=False)
    file_key: str = Field(nullable=False)
    upload_type: UploadType = Field(nullable=False)

    post: Post = Relationship(back_populates="image")
