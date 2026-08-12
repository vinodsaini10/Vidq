from fastapi import APIRouter, Depends
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/analysis")
async def get_competitor_analysis(current_user: User = Depends(get_current_user)):
    return {
        "trackedCompetitors": [
            {
                "channel": "Tech Lead Pro",
                "subscribers": "450,000",
                "avgViewsPerHour": "3,400 VPH",
                "outlierVideo": "How I Made $1M in AI Software",
                "outlierScore": "4.8x Channel Average"
            },
            {
                "channel": "Code with Dev",
                "subscribers": "280,000",
                "avgViewsPerHour": "1,800 VPH",
                "outlierVideo": "FastAPI vs Express Benchmark Test",
                "outlierScore": "3.2x Channel Average"
            }
        ],
        "contentGaps": [
            "Python 3.13 free threading benchmark deep-dives",
            "Building local AI agents with Gemini 3.6 Flash",
            "Microservice docker compose production deployments"
        ]
    }
