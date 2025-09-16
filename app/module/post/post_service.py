from sqlalchemy.ext.asyncio import AsyncSession

from app.api.post.v1.schema import PostRequest
from app.database.generic_repository import GenericRepository
from app.model.post import Post, PostImage
from app.module.media.enums import UploadType


class PostService:
    def __init__(self):
        self.post_repository = GenericRepository(Post)
        self.post_image_repository = GenericRepository(PostImage)

    async def upsert_post(
        self,
        user_social_id: str,
        post_request: PostRequest,
        session: AsyncSession,
    ) -> None:
        post = await self.post_repository.upsert(
            session,
            conflict_keys=["social_id", "mission_id"],
            return_instance=True,
            social_id=user_social_id,
            mission_id=post_request.mission_id,
            content=post_request.content,
        )

        if post and post.id and post_request.image_key:
            await self.post_image_repository.delete_by_field(session, post_id=post.id)

            upload_type = UploadType.from_file_key(post_request.image_key)
            await self.post_image_repository.create(
                session,
                post_id=post.id,
                file_key=post_request.image_key,
                upload_type=upload_type,
            )
