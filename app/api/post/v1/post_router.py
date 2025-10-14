from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.post.v1.schema import PostInfoResponse, PostLikeResponse, PostRequest, PostResponse
from app.database.dependency import get_db_session
from app.module.auth.dependency import verify_access_token
from app.module.auth.schemas import JWTPayload
from app.module.badge.badge_service import BadgeService
from app.module.post.post_service import PostService

post_router = APIRouter(prefix="/v1")


@post_router.post(
    "/",
    summary="게시물을 생성합니다",
    description="텍스트와 이미지가 포함된 게시물을 생성합니다.",
    status_code=status.HTTP_201_CREATED,
    response_model=PostResponse,
)
async def add_post(
    request_data: PostRequest,
    payload: JWTPayload = Depends(verify_access_token),
    session: AsyncSession = Depends(get_db_session),
    post_service: PostService = Depends(),
    badge_service: BadgeService = Depends(),
):
    await post_service.add_post(
        user_id=payload.user_id,
        post_request=request_data,
        session=session,
    )

    await badge_service.initial_badge(session, payload.user_id)

    return PostResponse(success=True, status_code=status.HTTP_201_CREATED)


@post_router.get(
    "/{post_id}",
    summary="게시물 상세 정보 조회",
    description="게시물의 상세 정보를 반환합니다.",
    status_code=status.HTTP_200_OK,
    response_model=PostInfoResponse,
)
async def get_post_info(
    post_id: int,
    payload: JWTPayload = Depends(verify_access_token),
    session: AsyncSession = Depends(get_db_session),
    post_service: PostService = Depends(),
) -> PostInfoResponse:
    return await post_service.get_post_info(session, post_id)


@post_router.post(
    "/{post_id}/like",
    summary="게시물 좋아요 토글",
    description="게시물에 좋아요를 추가하거나 취소합니다.",
    status_code=status.HTTP_200_OK,
    response_model=PostLikeResponse,
)
async def toggle_post_like(
    post_id: int,
    payload: JWTPayload = Depends(verify_access_token),
    session: AsyncSession = Depends(get_db_session),
    post_service: PostService = Depends(),
) -> PostLikeResponse:
    is_liked, like_count = await post_service.toggle_post_like(session, payload.user_id, post_id)
    return PostLikeResponse(is_liked=is_liked, like_count=like_count)
