from unittest.mock import AsyncMock, Mock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.post.v1.schema import PostRequest
from app.database.generic_repository import GenericRepository
from app.model.post import Post
from app.module.media.enums import UploadType
from app.module.post.post_service import PostService


@pytest.fixture
def post_service():
    with patch("app.module.post.post_service.MediaService"):
        service = PostService()
        service.post_repository = Mock(spec=GenericRepository)
        service.post_image_repository = Mock(spec=GenericRepository)
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
        mock_post = Mock(spec=Post)
        mock_post.id = 1
        post_service.post_repository.create = AsyncMock(return_value=mock_post)
        post_service.post_image_repository.create = AsyncMock()

        # when
        await post_service.add_post(user_id=123, post_request=post_request, session=mock_session)

        # then
        post_service.post_repository.create.assert_called_once_with(
            mock_session,
            return_instance=True,
            user_id=123,
            mission_id=1,
            content="테스트 게시물",
        )
        post_service.media_service.mark_file_as_confirmed.assert_called_once_with("content/2025-09-16/test.jpg")
        post_service.post_image_repository.create.assert_called_once_with(
            mock_session, post_id=1, file_key="content/2025-09-16/test.jpg", upload_type=UploadType.CONTENT
        )

    @pytest.mark.asyncio
    async def test_add_post_without_image(self, post_service, mock_session, post_request_without_image):
        # given
        mock_post = Mock(spec=Post)
        mock_post.id = 1
        post_service.post_repository.create = AsyncMock(return_value=mock_post)
        post_service.post_image_repository.create = AsyncMock()

        # when
        await post_service.add_post(user_id=123, post_request=post_request_without_image, session=mock_session)

        # then
        post_service.post_repository.create.assert_called_once_with(
            mock_session,
            return_instance=True,
            user_id=123,
            mission_id=1,
            content="테스트 게시물",
        )
        post_service.media_service.mark_file_as_confirmed.assert_not_called()
        post_service.post_image_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_add_post_with_profile_image_type(self, post_service, mock_session):
        # given
        profile_request = PostRequest(
            mission_id=2, content="프로필 이미지 테스트", image_key="profile/2025-09-16/profile.jpg"
        )
        mock_post = Mock(spec=Post)
        mock_post.id = 3
        post_service.post_repository.create = AsyncMock(return_value=mock_post)
        post_service.post_image_repository.create = AsyncMock()

        # when
        await post_service.add_post(user_id=789, post_request=profile_request, session=mock_session)

        # then
        post_service.post_image_repository.create.assert_called_once_with(
            mock_session, post_id=3, file_key="profile/2025-09-16/profile.jpg", upload_type=UploadType.PROFILE
        )
