from fastapi import APIRouter, Depends
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/channel-stats")
async def get_channel_analytics(current_user: User = Depends(get_current_user)):
    return {
        "viewsChart": [
            {"date": "May 1", "views": 12400, "revenue": 85},
            {"date": "May 5", "views": 18200, "revenue": 140},
            {"date": "May 10", "views": 24500, "revenue": 210},
            {"date": "May 15", "views": 31000, "revenue": 290},
            {"date": "May 20", "views": 42000, "revenue": 410},
            {"date": "May 25", "views": 58000, "revenue": 580},
            {"date": "May 30", "views": 74000, "revenue": 720},
        ],
        "ctrBreakdown": {
            "overallCtr": 8.4,
            "browseFeaturesCtr": 9.2,
            "suggestedVideosCtr": 7.8,
            "youtubeSearchCtr": 8.9
        },
        "audienceRetention": {
            "avgViewDuration": "06:42",
            "retentionAt30s": "74%",
            "topPerformingLength": "12-15 mins"
        }
    }
