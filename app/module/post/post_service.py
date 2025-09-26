from sqlalchemy.ext.asyncio import AsyncSession

from app.api.post.v1.schema import PostRequest
from app.database.generic_repository import GenericRepository
from app.model.post import Post, PostImage
from app.module.media.enums import UploadType
from app.module.media.media_service import MediaService


class PostService:
    def __init__(self):
        self.post_repository = GenericRepository(Post)
        self.post_image_repository = GenericRepository(PostImage)
        self.media_service = MediaService()

    async def add_post(
        self,
        user_id: int,
        post_request: PostRequest,
        session: AsyncSession,
    ) -> None:
        post = await self.post_repository.create(
            session,
            return_instance=True,
            user_id=user_id,
            mission_id=post_request.mission_id,
            content=post_request.content,
        )

        if post_request.image_key:
            self.media_service.mark_file_as_confirmed(post_request.image_key)

            upload_type = UploadType.from_file_key(post_request.image_key)
            await self.post_image_repository.create(
                session,
                post_id=post.id,
                file_key=post_request.image_key,
                upload_type=upload_type,
            )
