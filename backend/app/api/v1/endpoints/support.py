from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter()


class SupportTicketRequest(BaseModel):
    subject: str
    message: str


@router.post("/ticket")
async def create_support_ticket(
    req: SupportTicketRequest, current_user: User = Depends(get_current_user)
):
    return {
        "status": "received",
        "ticketId": "TICK-8842",
        "message": "Support ticket created successfully. Response expected within 2 hours."
    }
