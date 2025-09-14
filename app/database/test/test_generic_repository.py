from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.generic_repository import GenericRepository
from app.model.user import UserConsent


class TestGenericRepository:
    @pytest.fixture
    def mock_session(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def user_consent_repository(self):
        return GenericRepository(UserConsent)

    @pytest.fixture
    def sample_consent_data(self):
        return {
            "user_id": 1,
            "event": "marketing",
            "agree": True,
        }

    @pytest.fixture
    def sample_consent_instance(self):
        consent = UserConsent()
        consent.id = 1
        consent.user_id = 1
        consent.event = "marketing"
        consent.agree = True
        return consent

    # ===== upsert 메서드 테스트 =====
    @pytest.mark.asyncio
    async def test_upsert_success_without_return_instance(
        self, user_consent_repository, mock_session, sample_consent_data
    ):
        """upsert 메서드가 return_instance=False일 때 정상 동작하는지 테스트"""
        # Given
        conflict_keys = ["user_id", "event"]
        mock_session.execute = AsyncMock()
        mock_session.flush = AsyncMock()

        # When
        result = await user_consent_repository.upsert(
            session=mock_session, conflict_keys=conflict_keys, return_instance=False, **sample_consent_data
        )

        # Then
        assert result is None
        mock_session.execute.assert_called_once()
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_upsert_success_with_return_instance(
        self, user_consent_repository, mock_session, sample_consent_data, sample_consent_instance
    ):
        """upsert 메서드가 return_instance=True일 때 인스턴스를 반환하는지 테스트"""
        # Given
        conflict_keys = ["user_id", "event"]
        mock_session.execute = AsyncMock()
        mock_session.flush = AsyncMock()
        user_consent_repository.find_one = AsyncMock(return_value=sample_consent_instance)

        # When
        result = await user_consent_repository.upsert(
            session=mock_session, conflict_keys=conflict_keys, return_instance=True, **sample_consent_data
        )

        # Then
        assert result == sample_consent_instance
        mock_session.execute.assert_called_once()
        mock_session.flush.assert_called_once()
        user_consent_repository.find_one.assert_called_once_with(mock_session, user_id=1, event="marketing")

    @pytest.mark.asyncio
    async def test_upsert_with_update_dict(
        self, user_consent_repository, mock_session, sample_consent_data, sample_consent_instance
    ):
        """upsert에서 update_dict가 올바르게 생성되는지 테스트"""
        # Given
        conflict_keys = ["user_id", "event"]
        mock_session.execute = AsyncMock()
        mock_session.flush = AsyncMock()
        user_consent_repository.find_one = AsyncMock(return_value=sample_consent_instance)

        # When
        await user_consent_repository.upsert(session=mock_session, conflict_keys=conflict_keys, **sample_consent_data)

        # Then
        # execute가 호출되었는지 확인
        assert mock_session.execute.called
        # flush가 호출되었는지 확인
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_upsert_no_update_dict_when_only_conflict_keys(
        self, user_consent_repository, mock_session, sample_consent_instance
    ):
        """conflict_keys만 있을 때 update_dict가 빈 딕셔너리인지 테스트"""
        # Given
        conflict_keys = ["user_id", "event"]
        data = {"user_id": 1, "event": "marketing"}  # conflict_keys만 포함
        mock_session.execute = AsyncMock()
        mock_session.flush = AsyncMock()
        user_consent_repository.find_one = AsyncMock(return_value=sample_consent_instance)

        # When
        result = await user_consent_repository.upsert(
            session=mock_session, conflict_keys=conflict_keys, return_instance=False, **data
        )

        # Then
        assert result is None  # return_instance=False이므로 None
        mock_session.execute.assert_called_once()
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_upsert_find_one_returns_none(self, user_consent_repository, mock_session, sample_consent_data):
        """find_one이 None을 반환할 때 테스트"""
        # Given
        conflict_keys = ["user_id", "event"]
        mock_session.execute = AsyncMock()
        mock_session.flush = AsyncMock()
        user_consent_repository.find_one = AsyncMock(return_value=None)

        # When
        result = await user_consent_repository.upsert(
            session=mock_session, conflict_keys=conflict_keys, return_instance=True, **sample_consent_data
        )

        # Then
        assert result is None
        mock_session.execute.assert_called_once()
        mock_session.flush.assert_called_once()
        user_consent_repository.find_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_upsert_session_execute_failure(self, user_consent_repository, mock_session, sample_consent_data):
        """session.execute 실패 시 예외 전파 테스트"""
        # Given
        conflict_keys = ["user_id", "event"]
        mock_session.execute = AsyncMock(side_effect=Exception("Execute failed"))
        mock_session.flush = AsyncMock()

        # When & Then
        with pytest.raises(Exception) as exc_info:
            await user_consent_repository.upsert(
                session=mock_session, conflict_keys=conflict_keys, **sample_consent_data
            )

        assert str(exc_info.value) == "Execute failed"
        mock_session.execute.assert_called_once()
        mock_session.flush.assert_not_called()

    @pytest.mark.asyncio
    async def test_upsert_session_flush_failure(self, user_consent_repository, mock_session, sample_consent_data):
        """session.flush 실패 시 예외 전파 테스트"""
        # Given
        conflict_keys = ["user_id", "event"]
        mock_session.execute = AsyncMock()
        mock_session.flush = AsyncMock(side_effect=Exception("Flush failed"))

        # When & Then
        with pytest.raises(Exception) as exc_info:
            await user_consent_repository.upsert(
                session=mock_session, conflict_keys=conflict_keys, **sample_consent_data
            )

        assert str(exc_info.value) == "Flush failed"
        mock_session.execute.assert_called_once()
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_upsert_find_one_failure(self, user_consent_repository, mock_session, sample_consent_data):
        """find_one 실패 시 예외 전파 테스트"""
        # Given
        conflict_keys = ["user_id", "event"]
        mock_session.execute = AsyncMock()
        mock_session.flush = AsyncMock()
        user_consent_repository.find_one = AsyncMock(side_effect=Exception("Find failed"))

        # When & Then
        with pytest.raises(Exception) as exc_info:
            await user_consent_repository.upsert(
                session=mock_session, conflict_keys=conflict_keys, return_instance=True, **sample_consent_data
            )

        assert str(exc_info.value) == "Find failed"
        mock_session.execute.assert_called_once()
        mock_session.flush.assert_called_once()

    # ===== 기타 메서드들의 기본 동작 테스트 =====
    @pytest.mark.asyncio
    async def test_create_success(self, user_consent_repository, mock_session):
        """create 메서드 정상 동작 테스트"""
        # Given
        data = {"user_id": 1, "event": "marketing", "agree": True}
        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()

        # When
        result = await user_consent_repository.create(mock_session, **data)

        # Then
        assert result is not None
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_find_one_success(self, user_consent_repository, mock_session, sample_consent_instance):
        """find_one 메서드 정상 동작 테스트"""
        # Given
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_consent_instance
        mock_session.execute = AsyncMock(return_value=mock_result)

        # When
        result = await user_consent_repository.find_one(mock_session, user_id=1, event="marketing")

        # Then
        assert result == sample_consent_instance
        mock_session.execute.assert_called_once()
        mock_result.scalar_one_or_none.assert_called_once()

    @pytest.mark.asyncio
    async def test_repository_initialization(self):
        """Repository 초기화 테스트"""
        # When
        repository = GenericRepository(UserConsent)

        # Then
        assert repository.model == UserConsent
        assert hasattr(repository, "create")
        assert hasattr(repository, "find_one")
        assert hasattr(repository, "upsert")
        assert hasattr(repository, "update_instance")
