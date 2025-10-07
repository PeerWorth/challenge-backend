import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.challenge.v1.schema import MissionPost
from app.api.post.v1.schema import PostRequest
from app.common.utils.time import utc_now
from app.database.generic_repository import GenericRepository
from app.model.post import PostImage
from app.model.user import User
from app.module.challenge.challenge_repository import UserMissionRepository
from app.module.challenge.enums import MissionStatusType
from app.module.challenge.errors import UserMissionNotInProgressError
from app.module.media.enums import UploadType
from app.module.media.media_service import MediaService
from app.module.post.constants import INITIAL_POST_LIMIT
from app.module.post.post_repository import PostRepository


class PostService:
    def __init__(self):
        self.post_repository = PostRepository()
        self.post_image_repository = GenericRepository(PostImage)
        self.media_service = MediaService()
        self.user_mission_repository = UserMissionRepository()

    async def add_post(
        self,
        user_id: int,
        post_request: PostRequest,
        session: AsyncSession,
    ) -> None:
        mission_id = post_request.mission_id

        user_mission = await self.user_mission_repository.get_user_mission_in_progress(session, user_id, mission_id)
        if not user_mission:
            raise UserMissionNotInProgressError(user_id, mission_id)

        post = await self.post_repository.create(
            session,
            return_instance=True,
            user_id=user_id,
            mission_id=mission_id,
            content=post_request.content,
        )

        if post_request.image_key:
            await self.post_image_repository.create(
                session,
                post_id=post.id,  # type: ignore
                file_key=post_request.image_key,
                upload_type=UploadType.from_file_key(post_request.image_key),
            )

        await self.user_mission_repository.update(
            session,
            user_mission.id,  # type: ignore
            status=MissionStatusType.COMPLETED,
            post_id=post.id,  # type: ignore
            completed_at=utc_now(),
        )

    async def get_recent_mission_posts_with_images(
        self, session: AsyncSession, mission_id: int, limit: int = INITIAL_POST_LIMIT
    ) -> list[MissionPost]:
        recent_posts = await self.post_repository.get_recent_posts_by_mission(session, mission_id, limit)

        tasks = [self._create_mission_post(post_id, user, post_image) for post_id, user, post_image in recent_posts]
        results = await asyncio.gather(*tasks)

        return results

    async def _create_mission_post(self, post_id: int, user: User, post_image: PostImage | None) -> MissionPost:
        image_url = None
        if post_image:
            image_url = await asyncio.to_thread(self.media_service.get_presigned_download_url, post_image.file_key)

        return MissionPost(
            user_id=user.id,
            post_id=post_id,
            nickname=user.nickname,
            image_url=image_url,
        )
