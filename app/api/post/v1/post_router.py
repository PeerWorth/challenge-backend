from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.post.v1.schema import PostRequest, PostResponse
from app.database.dependency import get_db_session
from app.module.auth.dependency import verify_access_token
from app.module.auth.schemas import JWTPayload
from app.module.post.post_service import PostService
from app.module.user.user_service import UserService

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
    user_service: UserService = Depends(),
):
    user = await user_service.get_user_id_by_social_id(session, payload.social_id)

    await post_service.add_post(
        user_id=user.id,
        post_request=request_data,
        session=session,
    )
    return PostResponse(success=True, status_code=status.HTTP_201_CREATED)
