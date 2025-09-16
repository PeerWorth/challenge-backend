from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.post.v1.schema import PostRequest, PostResponse
from app.database.dependency import get_db_session
from app.module.auth.dependency import verify_access_token
from app.module.post.post_service import PostService

post_router = APIRouter(prefix="/v1")


@post_router.post(
    "/",
    summary="게시물을 생성 또는 업데이트합니다",
    description="텍스트와 이미지가 포함된 게시물을 생성하거나 업데이트합니다.",
    status_code=status.HTTP_201_CREATED,
    response_model=PostResponse,
)
async def upsert_post(
    request_data: PostRequest,
    current_user_social_id: str = Depends(verify_access_token),
    session: AsyncSession = Depends(get_db_session),
    post_service: PostService = Depends(),
):
    await post_service.upsert_post(
        user_social_id=current_user_social_id,
        post_request=request_data,
        session=session,
    )
    return PostResponse(success=True, status_code=status.HTTP_201_CREATED)
