from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter()


class SettingsUpdateRequest(BaseModel):
    theme: str = "dark"
    emailNotifications: bool = True
    weeklyReports: bool = True


@router.get("/")
async def get_settings(current_user: User = Depends(get_current_user)):
    return {
        "preferences": current_user.preferences,
        "youtubeChannelConnected": True,
        "channelHandle": current_user.youtube_handle or "@alexriverstech"
    }


@router.post("/")
async def update_settings(
    req: SettingsUpdateRequest, current_user: User = Depends(get_current_user)
):
    return {
        "status": "updated",
        "preferences": req.dict()
    }
