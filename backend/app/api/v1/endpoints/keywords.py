from fastapi import APIRouter, Depends
from app.dependencies.auth import get_current_user
from app.schemas.keyword import KeywordSearchRequest, KeywordResult
from app.models.user import User

router = APIRouter()


@router.post("/search", response_model=KeywordResult)
async def search_keywords(
    req: KeywordSearchRequest, current_user: User = Depends(get_current_user)
):
    kw = req.keyword.lower().strip()
    return KeywordResult(
        keyword=kw,
        search_volume=84200,
        competition_score=0.42,  # Low/Medium competition
        opportunity_score=88,    # High viral opportunity
        related_keywords=[
            f"{kw} tutorial 2026",
            f"best {kw} tools",
            f"how to learn {kw}",
            f"{kw} vs traditional coding",
            f"make money with {kw}"
        ]
    )
