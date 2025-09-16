from fastapi import APIRouter, Depends, status

from app.api.media.v1.schema import S3UrlRequest, S3UrlResponse
from app.module.auth.dependency import verify_access_token
from app.module.media.media_service import MediaService

user_router = APIRouter(prefix="/v1")


@user_router.post(
    "/presigned-url",
    summary="S3 presigned URL을 반환합니다",
    description="클라이언트가 S3에 직접 파일을 업로드할 수 있는 presigned URL을 생성하여 반환합니다.",
    status_code=status.HTTP_200_OK,
    response_model=S3UrlResponse,
)
async def create_presigned_url(
    request_data: S3UrlRequest,
    current_user_social_id: str = Depends(verify_access_token),
    media_service: MediaService = Depends(),
):
    url_info = media_service.create_presigned_upload_url(
        user_id=current_user_social_id,
        upload_type=request_data.upload_type,
    )

    return S3UrlResponse(
        upload_url=url_info["upload_url"],
        file_url=url_info["file_url"],
        expires_in=url_info["expires_in"],
        fields=url_info["fields"],
    )
