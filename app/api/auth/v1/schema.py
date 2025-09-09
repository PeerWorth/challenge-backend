from pydantic import BaseModel


class OAuthRequest(BaseModel):
    id_token: str
    
    
class OAuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    is_new_user: bool
    
        