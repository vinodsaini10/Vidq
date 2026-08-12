from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter()


class SEOAuditRequest(BaseModel):
    title: str
    description: str
    tags: str


@router.post("/audit")
async def audit_video_seo(
    req: SEOAuditRequest, current_user: User = Depends(get_current_user)
):
    title_score = 92 if len(req.title) >= 30 else 65
    desc_score = 88 if len(req.description) >= 100 else 55
    tag_score = 85 if len(req.tags.split(",")) >= 10 else 60

    overall = int((title_score * 0.4) + (desc_score * 0.4) + (tag_score * 0.2))

    return {
        "overallScore": overall,
        "titleGrade": "A" if title_score > 85 else "B",
        "descriptionGrade": "A" if desc_score > 85 else "C",
        "tagDensityGrade": "A" if tag_score > 85 else "B",
        "recommendations": [
            "Include target primary keyword within the first 60 characters of the title.",
            "Add timestamps in description for YouTube chapter indexing.",
            "Include 3 relevant hashtags at the bottom of the video description."
        ]
    }
