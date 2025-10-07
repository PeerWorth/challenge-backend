from unittest.mock import AsyncMock, Mock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.post.v1.schema import PostRequest
from app.database.generic_repository import GenericRepository
from app.model.post import Post
from app.model.user_challenge import UserMission
from app.module.challenge.enums import MissionStatusType
from app.module.media.enums import UploadType
from app.module.post.post_service import PostService


@pytest.fixture
def post_service():
    with patch("app.module.post.post_service.MediaService"):
        service = PostService()
        service.post_repository = Mock(spec=GenericRepository)
        service.post_image_repository = Mock(spec=GenericRepository)
        service.user_mission_repository = Mock(spec=GenericRepository)
        service.media_service = Mock()
    return service


@pytest.fixture
def mock_session():
    return Mock(spec=AsyncSession)


@pytest.fixture
def post_request():
    return PostRequest(mission_id=1, content="테스트 게시물", image_key="content/2025-09-16/test.jpg")


@pytest.fixture
def post_request_without_image():
    return PostRequest(mission_id=1, content="테스트 게시물", image_key=None)


class TestPostService:
    @pytest.mark.asyncio
    async def test_add_post_with_image(self, post_service, mock_session, post_request):
        # given
        mock_user_mission = Mock(spec=UserMission)
        mock_user_mission.id = 10
        mock_post = Mock(spec=Post)
        mock_post.id = 1
        post_service.user_mission_repository.get_user_mission_in_progress = AsyncMock(return_value=mock_user_mission)
        post_service.post_repository.create = AsyncMock(return_value=mock_post)
        post_service.post_image_repository.create = AsyncMock()
        post_service.user_mission_repository.update = AsyncMock()

        # when
        await post_service.add_post(user_id=123, post_request=post_request, session=mock_session)

        # then
        post_service.user_mission_repository.get_user_mission_in_progress.assert_called_once_with(mock_session, 123, 1)
        post_service.post_repository.create.assert_called_once_with(
            mock_session,
            return_instance=True,
            user_id=123,
            mission_id=1,
            content="테스트 게시물",
        )
        post_service.post_image_repository.create.assert_called_once_with(
            mock_session, post_id=1, file_key="content/2025-09-16/test.jpg", upload_type=UploadType.CONTENT
        )
        post_service.user_mission_repository.update.assert_called_once()
        call_args = post_service.user_mission_repository.update.call_args
        assert call_args[0][0] == mock_session
        assert call_args[0][1] == 10
        assert call_args[1]["status"] == MissionStatusType.COMPLETED
        assert call_args[1]["post_id"] == 1

    @pytest.mark.asyncio
    async def test_add_post_without_image(self, post_service, mock_session, post_request_without_image):
        # given
        mock_user_mission = Mock(spec=UserMission)
        mock_user_mission.id = 20
        mock_post = Mock(spec=Post)
        mock_post.id = 1
        post_service.user_mission_repository.get_user_mission_in_progress = AsyncMock(return_value=mock_user_mission)
        post_service.post_repository.create = AsyncMock(return_value=mock_post)
        post_service.post_image_repository.create = AsyncMock()
        post_service.user_mission_repository.update = AsyncMock()

        # when
        await post_service.add_post(user_id=123, post_request=post_request_without_image, session=mock_session)

        # then
        post_service.user_mission_repository.get_user_mission_in_progress.assert_called_once_with(mock_session, 123, 1)
        post_service.post_repository.create.assert_called_once_with(
            mock_session,
            return_instance=True,
            user_id=123,
            mission_id=1,
            content="테스트 게시물",
        )
        post_service.post_image_repository.create.assert_not_called()
        post_service.user_mission_repository.update.assert_called_once()
        call_args = post_service.user_mission_repository.update.call_args
        assert call_args[0][1] == 20
        assert call_args[1]["status"] == MissionStatusType.COMPLETED

    @pytest.mark.asyncio
    async def test_add_post_with_profile_image_type(self, post_service, mock_session):
        # given
        profile_request = PostRequest(
            mission_id=2, content="프로필 이미지 테스트", image_key="profile/2025-09-16/profile.jpg"
        )
        mock_user_mission = Mock(spec=UserMission)
        mock_user_mission.id = 30
        mock_post = Mock(spec=Post)
        mock_post.id = 3
        post_service.user_mission_repository.get_user_mission_in_progress = AsyncMock(return_value=mock_user_mission)
        post_service.post_repository.create = AsyncMock(return_value=mock_post)
        post_service.post_image_repository.create = AsyncMock()
        post_service.user_mission_repository.update = AsyncMock()

        # when
        await post_service.add_post(user_id=789, post_request=profile_request, session=mock_session)

        # then
        post_service.post_image_repository.create.assert_called_once_with(
            mock_session, post_id=3, file_key="profile/2025-09-16/profile.jpg", upload_type=UploadType.PROFILE
        )
        post_service.user_mission_repository.update.assert_called_once()
