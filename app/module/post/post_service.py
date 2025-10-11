import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.challenge.v1.schema import MissionPost
from app.api.post.v1.schema import PostRequest
from app.common.utils.time import utc_now
from app.database.generic_repository import GenericRepository
from app.model.post import PostImage
from app.model.user import User
from app.module.challenge.challenge_repository import (
    ChallengeRepository,
    UserChallengeRepository,
    UserMissionRepository,
)
from app.module.challenge.enums import ChallengeStatusType, MissionStatusType
from app.module.challenge.errors import UserMissionNotInProgressError
from app.module.media.enums import UploadType
from app.module.media.media_service import MediaService
from app.module.post.post_repository import PostRepository


class PostService:
    def __init__(self):
        self.post_repository = PostRepository()
        self.post_image_repository = GenericRepository(PostImage)
        self.media_service = MediaService()
        self.user_mission_repository = UserMissionRepository()
        self.user_challenge_repository = UserChallengeRepository()
        self.challenge_repository = ChallengeRepository()

    async def add_post(
        self,
        user_id: int,
        post_request: PostRequest,
        session: AsyncSession,
    ) -> None:
        user_mission = await self._validate_user_mission(session, user_id, post_request.mission_id)

        post = await self.post_repository.create(
            session,
            return_instance=True,
            user_id=user_id,
            mission_id=post_request.mission_id,
            content=post_request.content,
        )

        await self._create_post_image_if_exists(session, post.id, post_request.image_key)  # type: ignore

        await self.user_mission_repository.update(
            session,
            user_mission.id,  # type: ignore
            status=MissionStatusType.COMPLETED,
            post_id=post.id,  # type: ignore
            completed_at=utc_now(),
        )

        await self._complete_challenge_if_finished(session, user_mission.user_challenge_id)

    async def _validate_user_mission(self, session: AsyncSession, user_id: int, mission_id: int):
        user_mission = await self.user_mission_repository.get_user_mission_in_progress(session, user_id, mission_id)
        if not user_mission:
            raise UserMissionNotInProgressError(user_id, mission_id)
        return user_mission

    async def _create_post_image_if_exists(self, session: AsyncSession, post_id: int, image_key: str | None) -> None:
        if image_key:
            await self.post_image_repository.create(
                session,
                post_id=post_id,
                file_key=image_key,
                upload_type=UploadType.from_file_key(image_key),
            )

    async def _complete_challenge_if_finished(self, session: AsyncSession, user_challenge_id: int) -> None:
        user_challenge = await self.user_challenge_repository.get_by_id(session, user_challenge_id)
        if not user_challenge:
            return

        is_finished = await self._is_challenge_finished(session, user_challenge)
        if is_finished:
            await self.user_challenge_repository.update(
                session, user_challenge.id, status=ChallengeStatusType.COMPLETED  # type: ignore
            )

    async def _is_challenge_finished(self, session: AsyncSession, user_challenge) -> bool:
        challenge_missions = await self.challenge_repository.get_challenge_missions(
            session, user_challenge.challenge_id
        )
        completed_count = await self.user_mission_repository.count(
            session, user_challenge_id=user_challenge.id, status=MissionStatusType.COMPLETED
        )
        return completed_count == len(challenge_missions)

    async def get_recent_mission_posts_with_images(
        self, session: AsyncSession, mission_id: int, limit: int
    ) -> list[MissionPost]:
        recent_posts = await self.post_repository.get_recent_posts_by_mission(session, mission_id, limit)

        tasks = [self._create_mission_post(post_id, user, post_image) for post_id, user, post_image in recent_posts]
        results = await asyncio.gather(*tasks)

        return results

    async def get_mission_posts_paginated(
        self, session: AsyncSession, mission_id: int, limit: int, cursor: int | None = None
    ) -> list[MissionPost]:
        posts = await self.post_repository.get_posts_by_mission_with_cursor(session, mission_id, limit, cursor)

        tasks = [self._create_mission_post(post_id, user, post_image) for post_id, user, post_image in posts]
        results = await asyncio.gather(*tasks)

        return results

    async def _create_mission_post(self, post_id: int, user: User, post_image: PostImage | None) -> MissionPost:
        image_url = None
        if post_image:
            image_url = await asyncio.to_thread(self.media_service.get_presigned_view_url, post_image.file_key)

        return MissionPost(
            user_id=user.id,
            post_id=post_id,
            nickname=user.nickname,
            image_url=image_url,
        )
