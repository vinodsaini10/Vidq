from fastapi import APIRouter, Depends
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/list")
async def list_reports(current_user: User = Depends(get_current_user)):
    return [
        {
            "id": "rep-001",
            "title": "30-Day Channel Health & Revenue Audit",
            "type": "PDF Executive Summary",
            "size": "2.4 MB",
            "date": "May 2025 Audit",
            "downloadUrl": "/api/v1/reports/download/rep-001"
        },
        {
            "id": "rep-002",
            "title": "Competitor Gap & Content Velocity Analysis",
            "type": "CSV Data Export",
            "size": "1.1 MB",
            "date": "Weekly Snapshot",
            "downloadUrl": "/api/v1/reports/download/rep-002"
        }
    ]
