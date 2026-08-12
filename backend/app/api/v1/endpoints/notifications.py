from fastapi import APIRouter, Depends
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/feed")
async def get_notifications(current_user: User = Depends(get_current_user)):
    return [
        {
            "id": "notif-1",
            "title": "🎉 100,000 Subscribers Milestone!",
            "message": "Your channel just crossed 100K subscribers! Download your growth badge in Reports.",
            "time": "2 hours ago",
            "type": "milestone",
            "read": False
        },
        {
            "id": "notif-2",
            "title": "⚡ Viral Outlier Alert Detected",
            "message": "Competitor Tech Lead Pro released a video gaining +4,200 views/hr on 'Gemini 3.6'.",
            "time": "5 hours ago",
            "type": "alert",
            "read": False
        },
        {
            "id": "notif-3",
            "title": "🤖 AI Content Strategy Ready",
            "message": "VidPulse AI generated 3 video script drafts tailored for next week's tech trends.",
            "time": "1 day ago",
            "type": "ai",
            "read": True
        }
    ]
