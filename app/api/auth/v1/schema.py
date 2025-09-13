from app.common.schema import CamelBaseModel


class OAuthRequest(CamelBaseModel):
    id_token: str


class OAuthResponse(CamelBaseModel):
    access_token: str
    refresh_token: str
    is_new_user: bool
