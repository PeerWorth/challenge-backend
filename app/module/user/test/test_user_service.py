from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.user.v1.schema import ProfileRequest
from app.model.user import User, UserConsent
from app.module.user.enums import AgreeTypes, GenderTypes
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
        user.birth_year = 1990
        user.gender = GenderTypes.MAN
        return user

    @pytest.fixture
    def updated_user(self):
        user = User()
        user.id = 1
        user.social_id = "test_social_id_123"
        user.nickname = "새닉네임"
        user.birth_year = 1995
        user.gender = GenderTypes.WOMAN
        return user

    @pytest.fixture
    def profile_request(self):
        return ProfileRequest(nickname="새닉네임", birth_year=1995, gender=GenderTypes.WOMAN)

    @pytest.fixture
    def user_consent(self):
        consent = UserConsent()
        consent.id = 1
        consent.user_id = 1
        consent.event = "marketing"
        consent.agree = True
        return consent

    # ===== update_user_profile 테스트 =====
    @pytest.mark.asyncio
    async def test_update_user_profile_success_with_kwargs(self, user_service: UserService, mock_session, sample_user):
        """update_user_profile이 **kwargs 방식으로 잘 동작하는지 테스트"""
        # Given
        user_id = 1
        user_service.user_repository.get_by_id = AsyncMock(return_value=sample_user)
        user_service.user_repository.update_instance = AsyncMock(return_value=None)

        # When
        await user_service.update_user_profile(
            session=mock_session,
            user_id=user_id,
            nickname="새닉네임",
            birth_year=1995,
            gender=GenderTypes.WOMAN,
        )

        # Then
        user_service.user_repository.get_by_id.assert_called_once_with(mock_session, user_id)
        user_service.user_repository.update_instance.assert_called_once_with(
            session=mock_session,
            instance=sample_user,
            nickname="새닉네임",
            birth_year=1995,
            gender=GenderTypes.WOMAN,
        )

    @pytest.mark.asyncio
    async def test_update_user_profile_protected_fields_filtered(
        self, user_service: UserService, mock_session, sample_user
    ):
        # Given
        user_id = 1
        user_service.user_repository.get_by_id = AsyncMock(return_value=sample_user)
        user_service.user_repository.update_instance = AsyncMock(return_value=None)

        # When - protected fields 포함해서 호출
        await user_service.update_user_profile(
            session=mock_session,
            user_id=user_id,
            nickname="새닉네임",
            provider="google",  # protected field
            id=999,  # protected field
        )

        # Then - protected fields는 제외되고 호출되어야 함
        user_service.user_repository.update_instance.assert_called_once_with(
            session=mock_session,
            instance=sample_user,
            nickname="새닉네임",  # only non-protected field
        )

    @pytest.mark.asyncio
    async def test_update_user_profile_user_not_found(self, user_service: UserService, mock_session):
        # Given
        user_id = 999
        user_service.user_repository.get_by_id = AsyncMock(return_value=None)

        # When & Then
        with pytest.raises(UserNotFoundException):
            await user_service.update_user_profile(
                session=mock_session,
                user_id=user_id,
                nickname="새닉네임",
            )

    @pytest.mark.asyncio
    async def test_upsert_user_consent_success(self, user_service: UserService, mock_session, user_consent) -> None:
        # Given
        user_service.user_consent_repository.upsert = AsyncMock(return_value=None)

        # When
        await user_service.upsert_user_consent(
            session=mock_session,
            user_id=1,
            event=AgreeTypes.MARKETING.value,
            agree=True,
        )

        # Then
        user_service.user_consent_repository.upsert.assert_called_once_with(
            session=mock_session,
            conflict_keys=["user_id", "event"],
            return_instance=False,  # 최적화 파라미터 추가
            user_id=1,
            event=AgreeTypes.MARKETING.value,
            agree=True,
        )

    @pytest.mark.asyncio
    async def test_register_user_profile_success(
        self, user_service: UserService, mock_session, sample_user, profile_request, user_consent
    ):
        # Given
        user_service.user_repository.get_by_id = AsyncMock(return_value=sample_user)
        user_service.user_repository.update_instance = AsyncMock(return_value=sample_user)
        user_service.user_consent_repository.upsert = AsyncMock(return_value=None)

        # When
        await user_service.register_user_profile(
            session=mock_session,
            user_id=1,
            request_data=profile_request,
        )

        # Then
        user_service.user_repository.get_by_id.assert_called_once_with(mock_session, 1)
        user_service.user_repository.update_instance.assert_called_once_with(
            session=mock_session,
            instance=sample_user,
            nickname="새닉네임",
            birth_year=1995,
            gender=GenderTypes.WOMAN,
        )

        assert user_service.user_consent_repository.upsert.call_count == 2

        calls = user_service.user_consent_repository.upsert.call_args_list

        assert calls[0][1] == {
            "session": mock_session,
            "conflict_keys": ["user_id", "event"],
            "return_instance": False,  # 추가
            "user_id": 1,
            "event": AgreeTypes.PERSONAL_INFO.value,
            "agree": True,
        }

        # Term of use consent
        assert calls[1][1] == {
            "session": mock_session,
            "conflict_keys": ["user_id", "event"],
            "return_instance": False,  # 추가
            "user_id": 1,
            "event": AgreeTypes.TERM_OF_USE.value,
            "agree": True,
        }

    @pytest.mark.asyncio
    async def test_register_user_profile_success_with_two_consents(
        self, user_service: UserService, mock_session, sample_user, user_consent
    ):
        # Given
        profile_request = ProfileRequest(nickname="새닉네임", birth_year=1995, gender=GenderTypes.WOMAN)

        user_service.user_repository.get_by_id = AsyncMock(return_value=sample_user)
        user_service.user_repository.update_instance = AsyncMock(return_value=sample_user)
        user_service.user_consent_repository.upsert = AsyncMock(return_value=None)

        # When
        await user_service.register_user_profile(
            session=mock_session,
            user_id=1,
            request_data=profile_request,
        )

        # Then
        user_service.user_repository.get_by_id.assert_called_once_with(mock_session, 1)

        # 2개의 consent만 호출되었는지 확인
        assert user_service.user_consent_repository.upsert.call_count == 2

    @pytest.mark.asyncio
    async def test_register_user_profile_user_not_found(self, user_service: UserService, mock_session, profile_request):
        # Given
        user_service.user_repository.get_by_id = AsyncMock(return_value=None)

        # When & Then
        with pytest.raises(UserNotFoundException):
            await user_service.register_user_profile(
                session=mock_session,
                user_id=999,
                request_data=profile_request,
            )

    @pytest.mark.asyncio
    async def test_register_user_profile_consent_upsert_failure(
        self, user_service: UserService, mock_session, sample_user, profile_request
    ):
        # Given
        user_service.user_repository.get_by_id = AsyncMock(return_value=sample_user)
        user_service.user_repository.update_instance = AsyncMock(return_value=sample_user)
        user_service.user_consent_repository.upsert = AsyncMock(side_effect=Exception("Consent upsert failed"))

        # When & Then
        with pytest.raises(Exception) as exc_info:
            await user_service.register_user_profile(
                session=mock_session,
                user_id=1,
                request_data=profile_request,
            )

        assert str(exc_info.value) == "Consent upsert failed"

    @pytest.mark.asyncio
    async def test_user_service_repositories_initialization(self, user_service: UserService):
        # Then
        assert user_service.user_repository is not None
        assert user_service.user_consent_repository is not None
        assert hasattr(user_service.user_repository, "find_by_field")
        assert hasattr(user_service.user_repository, "update_instance")
        assert hasattr(user_service.user_consent_repository, "upsert")
