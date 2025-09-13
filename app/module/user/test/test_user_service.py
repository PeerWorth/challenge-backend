from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.user import User
from app.module.user.error import UserNotFoundException
from app.module.user.user_service import UserService


class TestUserService:
    @pytest.fixture
    def user_service(self) -> UserService:
        return UserService()

    @pytest.fixture
    def mock_session(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def sample_user(self):
        user = User()
        user.id = 1
        user.social_id = "test_social_id_123"
        user.nickname = "기존닉네임"
        user.birthday = date(1990, 1, 1)
        user.gender = True
        user.phone = "01012345678"
        return user

    @pytest.fixture
    def updated_user(self):
        user = User()
        user.id = 1
        user.social_id = "test_social_id_123"
        user.nickname = "새닉네임"
        user.birthday = date(1995, 6, 15)
        user.gender = False
        user.phone = "01087654321"
        return user

    @pytest.fixture
    def profile_data(self):
        return {"nickname": "새닉네임", "birthday": date(1995, 6, 15), "gender": False, "phone": "01087654321"}

    @pytest.mark.asyncio
    async def test_update_user_profile_success(
        self, user_service: UserService, mock_session, sample_user, updated_user, profile_data
    ):
        # Given
        social_id = "test_social_id_123"

        user_service.user_repository.find_by_field = AsyncMock(return_value=sample_user)
        user_service.user_repository.update_instance = AsyncMock(return_value=updated_user)

        # When
        result = await user_service.update_user_profile(
            session=mock_session,
            social_id=social_id,
            nickname=profile_data["nickname"],
            birthday=profile_data["birthday"],
            gender=profile_data["gender"],
            phone=profile_data["phone"],
        )

        # Then
        assert result == updated_user
        user_service.user_repository.find_by_field.assert_called_once_with(mock_session, "social_id", social_id)
        user_service.user_repository.update_instance.assert_called_once_with(
            session=mock_session,
            instance=sample_user,
            nickname=profile_data["nickname"],
            birthday=profile_data["birthday"],
            gender=profile_data["gender"],
            phone=profile_data["phone"],
        )

    @pytest.mark.asyncio
    async def test_update_user_profile_user_not_found(self, user_service: UserService, mock_session, profile_data):
        """
        Given: 존재하지 않는 사용자의 social_id와 업데이트할 프로필 정보가 주어졌을 때
        When: update_user_profile 메서드를 호출하면
        Then: UserNotFoundException 예외가 발생한다
        """
        # Given
        social_id = "nonexistent_social_id"

        user_service.user_repository.find_by_field = AsyncMock(return_value=None)

        # When & Then
        with pytest.raises(UserNotFoundException) as exc_info:
            await user_service.update_user_profile(
                session=mock_session,
                social_id=social_id,
                nickname=profile_data["nickname"],
                birthday=profile_data["birthday"],
                gender=profile_data["gender"],
                phone=profile_data["phone"],
            )

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "사용자를 찾을 수 없습니다."

        user_service.user_repository.find_by_field.assert_called_once_with(mock_session, "social_id", social_id)

        assert True

    @pytest.mark.asyncio
    async def test_update_user_profile_with_different_data_types(
        self, user_service: UserService, mock_session, sample_user
    ):
        # Given
        social_id = "test_social_id_123"
        updated_user_mock = MagicMock()

        # Test data with various types
        nickname = "테스트닉네임"
        birthday = date(2000, 12, 25)
        gender = True
        phone = "01099999999"

        user_service.user_repository.find_by_field = AsyncMock(return_value=sample_user)
        user_service.user_repository.update_instance = AsyncMock(return_value=updated_user_mock)

        # When
        result = await user_service.update_user_profile(
            session=mock_session, social_id=social_id, nickname=nickname, birthday=birthday, gender=gender, phone=phone
        )

        # Then
        assert result == updated_user_mock
        user_service.user_repository.update_instance.assert_called_once_with(
            session=mock_session, instance=sample_user, nickname=nickname, birthday=birthday, gender=gender, phone=phone
        )

    @pytest.mark.asyncio
    async def test_update_user_profile_repository_dependency(self, user_service: UserService):
        # Given & When
        repository = user_service.user_repository

        # Then
        assert repository is not None
        assert hasattr(repository, "find_by_field")
        assert hasattr(repository, "update_instance")

    @pytest.mark.asyncio
    async def test_update_user_profile_edge_case_empty_strings(
        self, user_service: UserService, mock_session, sample_user
    ):
        # Given
        social_id = "test_social_id_123"
        updated_user_mock = MagicMock()

        # Edge case data
        nickname = ""  # empty string
        birthday = date(1990, 1, 1)
        gender = False
        phone = ""  # empty string

        user_service.user_repository.find_by_field = AsyncMock(return_value=sample_user)
        user_service.user_repository.update_instance = AsyncMock(return_value=updated_user_mock)

        # When
        result = await user_service.update_user_profile(
            session=mock_session, social_id=social_id, nickname=nickname, birthday=birthday, gender=gender, phone=phone
        )

        # Then
        assert result == updated_user_mock
        user_service.user_repository.update_instance.assert_called_once_with(
            session=mock_session, instance=sample_user, nickname="", birthday=birthday, gender=False, phone=""
        )

    @pytest.mark.asyncio
    async def test_update_user_profile_repository_exception_propagation(
        self, user_service: UserService, mock_session, sample_user
    ):
        # Given
        social_id = "test_social_id_123"
        repository_error = Exception("Database connection failed")

        user_service.user_repository.find_by_field = AsyncMock(return_value=sample_user)
        user_service.user_repository.update_instance = AsyncMock(side_effect=repository_error)

        # When & Then
        with pytest.raises(Exception) as exc_info:
            await user_service.update_user_profile(
                session=mock_session,
                social_id=social_id,
                nickname="닉네임",
                birthday=date(1990, 1, 1),
                gender=True,
                phone="01012345678",
            )

        assert str(exc_info.value) == "Database connection failed"
