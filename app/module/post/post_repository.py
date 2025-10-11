from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.generic_repository import GenericRepository
from app.model.post import Post, PostImage
from app.model.user import User


class PostRepository(GenericRepository):
    def __init__(self):
        super().__init__(Post)

    async def get_recent_posts_by_mission(
        self, session: AsyncSession, mission_id: int, limit: int = 6
    ) -> list[tuple[int, User, PostImage | None]]:
        stmt = (
            select(Post.id, Post.created_at, User, PostImage)  # type: ignore
            .join(User, Post.user_id == User.id)  # type: ignore
            .outerjoin(PostImage, PostImage.post_id == Post.id)  # type: ignore
            .where(Post.mission_id == mission_id)  # type: ignore
            .order_by(desc(Post.created_at))  # type: ignore
            .limit(limit)
        )

        result = await session.execute(stmt)
        rows = result.all()

        return [(post_id, user, post_image) for post_id, _, user, post_image in rows]

    async def get_posts_by_mission_with_cursor(
        self, session: AsyncSession, mission_id: int, limit: int, cursor: int | None = None
    ) -> list[tuple[int, User, PostImage | None]]:
        stmt = (
            select(Post.id, User, PostImage)  # type: ignore
            .join(User, Post.user_id == User.id)  # type: ignore
            .outerjoin(PostImage, PostImage.post_id == Post.id)  # type: ignore
            .where(Post.mission_id == mission_id)  # type: ignore
        )

        if cursor is not None:
            stmt = stmt.where(Post.id < cursor)  # type: ignore

        stmt = stmt.order_by(desc(Post.id)).limit(limit)  # type: ignore

        result = await session.execute(stmt)
        rows = result.all()

        return [(post_id, user, post_image) for post_id, user, post_image in rows]
