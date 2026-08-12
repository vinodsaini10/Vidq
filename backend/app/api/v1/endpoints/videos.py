from fastapi import APIRouter, Depends
from typing import List
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/list")
async def get_videos(current_user: User = Depends(get_current_user)):
    return [
        {
            "id": "vid-101",
            "title": "I Built a Full Stack SaaS in 24 Hours with Gemini 3.6",
            "status": "Published",
            "niche": "AI & Tech",
            "scheduledDate": "2025-06-12",
            "views": "142,500",
            "ctr": "9.4%",
            "seoScore": 96
        },
        {
            "id": "vid-102",
            "title": "Top 10 AI Tools Every Programmer Must Use in 2026",
            "status": "Scheduled",
            "niche": "Software Engineering",
            "scheduledDate": "2025-06-18",
            "views": "Pending",
            "ctr": "8.9% (Predicted)",
            "seoScore": 91
        },
        {
            "id": "vid-103",
            "title": "Why Python 3.13 is Destroying Other Languages",
            "status": "Editing",
            "niche": "Python Programming",
            "scheduledDate": "2025-06-25",
            "views": "In Production",
            "ctr": "9.1% (Predicted)",
            "seoScore": 88
        }
    ]
