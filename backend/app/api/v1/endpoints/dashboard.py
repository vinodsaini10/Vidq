from fastapi import APIRouter, Depends
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/overview")
async def get_dashboard_overview(current_user: User = Depends(get_current_user)):
    return {
        "channelName": current_user.youtube_channel_title or "Alex Rivers Tech",
        "subscribers": current_user.youtube_subscriber_count or 124500,
        "monthlyViews": 482100,
        "estimatedRevenue": 3420.50,
        "channelHealthScore": 92,
        "avgCtr": 8.4,
        "topNiche": "AI & Tech SaaS",
        "recentMilestones": [
            "Passed 100K Subscribers",
            "+24% CTR increase on latest video",
            "Top 5% in AI & Tech niche"
        ]
    }
