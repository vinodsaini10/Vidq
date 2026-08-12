import json
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.dependencies.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.models.ai import AIUsage, AIGenerationHistory
from app.services.ai.gateway import ai_gateway
from app.services.ai.tasks import ai_task_service
from app.services.ai.conversation import conversation_manager
from app.services.ai.credits import credit_system
from app.services.ai.registry import model_registry
from app.schemas.ai import (
    AIGenerateRequest,
    AIGenerateResponse,
    AIChatRequest,
    AIConversationCreateRequest,
    AIConversationRenameRequest,
    AIConversationResponse,
    AIMessageResponse,
    AIMessageFeedbackRequest,
    AITitleGenerateRequest,
    AIDescriptionGenerateRequest,
    AITagsGenerateRequest,
    AIHooksGenerateRequest,
    AIScriptGenerateRequest,
    AIIdeasGenerateRequest,
    AIThumbnailPromptRequest,
    AISEOAnalysisRequest,
    AICompetitorAnalysisRequest,
    AIChannelCoachRequest,
    AICreditsResponse,
    AIModelResponse,
    AIUsageSummaryResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


# ==========================================
# 1. LEGACY & GENERAL GENERATION ENDPOINT
# ==========================================

@router.post("/generate", response_model=AIGenerateResponse)
async def generate_ai_content(
    req: AIGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """General AI generation route with credit deduction and safety filtering."""
    res = await ai_gateway.generate(
        db=db,
        user_id=str(current_user.id),
        feature=req.type,
        prompt=req.prompt,
        system_prompt="You are an expert YouTube growth AI assistant.",
        credits_cost=1,
    )
    return AIGenerateResponse(
        result=res.text,
        source=res.model_used,
        tokens_used=res.total_tokens,
    )


# ==========================================
# 2. AI CHAT & CONVERSATIONS
# ==========================================

@router.get("/conversations", response_model=List[AIConversationResponse])
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    convs = await conversation_manager.list_conversations(db, str(current_user.id))
    return [
        AIConversationResponse(
            id=str(c.id),
            title=c.title,
            system_instruction=c.system_instruction,
            created_at=c.created_at,
            messages=[],
        )
        for c in convs
    ]


@router.post("/conversations", response_model=AIConversationResponse)
async def create_conversation(
    req: AIConversationCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conv = await conversation_manager.create_conversation(
        db, str(current_user.id), req.title or "New Chat", req.system_instruction
    )
    return AIConversationResponse(
        id=str(conv.id),
        title=conv.title,
        system_instruction=conv.system_instruction,
        created_at=conv.created_at,
        messages=[],
    )


@router.get("/conversations/{conversation_id}", response_model=AIConversationResponse)
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conv = await conversation_manager.get_conversation(db, str(current_user.id), conversation_id)
    msgs = [
        AIMessageResponse(
            id=str(m.id),
            conversation_id=str(m.conversation_id),
            sender=m.sender,
            content=m.content,
            tokens_used=m.tokens_used,
            feedback=m.feedback,
            created_at=m.created_at,
        )
        for m in conv.messages
    ]
    return AIConversationResponse(
        id=str(conv.id),
        title=conv.title,
        system_instruction=conv.system_instruction,
        created_at=conv.created_at,
        messages=msgs,
    )


@router.put("/conversations/{conversation_id}", response_model=AIConversationResponse)
async def rename_conversation(
    conversation_id: str,
    req: AIConversationRenameRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conv = await conversation_manager.rename_conversation(
        db, str(current_user.id), conversation_id, req.title
    )
    return AIConversationResponse(
        id=str(conv.id),
        title=conv.title,
        system_instruction=conv.system_instruction,
        created_at=conv.created_at,
        messages=[],
    )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await conversation_manager.delete_conversation(db, str(current_user.id), conversation_id)
    return {"message": "Conversation deleted successfully."}


@router.post("/chat")
async def send_chat_message(
    req: AIChatRequest,
    stream: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Sends a chat message in a conversation with optional SSE streaming."""
    user_id = str(current_user.id)

    # If conversation_id not supplied, create one automatically
    conv_id = req.conversation_id
    if not conv_id:
        conv = await conversation_manager.create_conversation(db, user_id, req.message[:30])
        conv_id = str(conv.id)

    if stream:
        async def event_generator():
            yield f"data: {json.dumps({'type': 'status', 'status': 'thinking'})}\n\n"
            async for chunk in ai_gateway.generate_stream(
                db=db,
                user_id=user_id,
                feature="chat_stream",
                prompt=req.message,
                model_name=req.model,
                credits_cost=1,
            ):
                yield f"data: {json.dumps({'type': 'token', 'content': chunk})}\n\n"
            yield f"data: {json.dumps({'type': 'completion', 'conversation_id': conv_id})}\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    msg = await conversation_manager.send_message(
        db=db,
        user_id=user_id,
        conversation_id=conv_id,
        user_content=req.message,
        model_name=req.model,
    )
    return {
        "conversation_id": conv_id,
        "message": AIMessageResponse(
            id=str(msg.id),
            conversation_id=str(msg.conversation_id),
            sender=msg.sender,
            content=msg.content,
            tokens_used=msg.tokens_used,
            feedback=msg.feedback,
            created_at=msg.created_at,
        ),
    }


@router.post("/feedback")
async def message_feedback(
    req: AIMessageFeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await conversation_manager.update_message_feedback(
        db, str(current_user.id), req.message_id, req.feedback
    )
    return {"message": "Feedback recorded."}


# ==========================================
# 3. YOUTUBE CONTENT GENERATION TOOLS
# ==========================================

@router.post("/generate/title")
async def generate_title(
    req: AITitleGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ai_task_service.generate_titles(
        db=db,
        user_id=str(current_user.id),
        topic=req.topic,
        audience=req.audience or "General",
        tone=req.tone or "Engaging",
        provider=req.provider,
        model=req.model,
    )


@router.post("/generate/description")
async def generate_description(
    req: AIDescriptionGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ai_task_service.generate_description(
        db=db,
        user_id=str(current_user.id),
        topic=req.topic,
        key_points=req.key_points or "",
        cta=req.cta or "Subscribe for more videos!",
    )


@router.post("/generate/tags")
async def generate_tags(
    req: AITagsGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ai_task_service.generate_tags(
        db=db, user_id=str(current_user.id), topic=req.topic, keywords=req.keywords or ""
    )


@router.post("/generate/hashtags")
async def generate_hashtags(
    req: AITagsGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ai_task_service.generate_hashtags(
        db=db, user_id=str(current_user.id), topic=req.topic
    )


@router.post("/generate/hooks")
async def generate_hooks(
    req: AIHooksGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ai_task_service.generate_hooks(
        db=db, user_id=str(current_user.id), topic=req.topic, audience=req.audience or "General"
    )


@router.post("/generate/script")
async def generate_script(
    req: AIScriptGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ai_task_service.generate_script(
        db=db,
        user_id=str(current_user.id),
        topic=req.topic,
        script_format=req.format or "5 minute",
        tone=req.tone or "Engaging",
    )


@router.post("/generate/ideas")
async def generate_ideas(
    req: AIIdeasGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ai_task_service.generate_ideas(
        db=db, user_id=str(current_user.id), niche=req.niche, audience=req.audience or "General"
    )


@router.post("/generate/thumbnail-prompt")
async def generate_thumbnail_prompt(
    req: AIThumbnailPromptRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ai_task_service.generate_thumbnail_prompt(
        db=db, user_id=str(current_user.id), topic=req.topic, emotion=req.emotion or "High Contrast"
    )


# ==========================================
# 4. ANALYTICS & SEO AI TOOLS
# ==========================================

@router.post("/analyze/seo")
async def analyze_seo(
    req: AISEOAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ai_task_service.analyze_seo(
        db=db,
        user_id=str(current_user.id),
        title=req.title,
        description=req.description or "",
        tags=req.tags or "",
        keywords=req.keywords or "",
    )


@router.post("/analyze/competitor")
async def analyze_competitors(
    req: AICompetitorAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ai_task_service.analyze_competitors(
        db=db, user_id=str(current_user.id), my_topic=req.my_topic
    )


@router.post("/coach")
async def channel_coach(
    req: AIChannelCoachRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ai_task_service.channel_coach(
        db=db, user_id=str(current_user.id), question=req.question
    )


# ==========================================
# 5. CREDITS, USAGE & MODELS METADATA
# ==========================================

@router.get("/credits", response_model=AICreditsResponse)
async def get_user_credits(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await credit_system.get_user_credits(db, str(current_user.id))


@router.get("/models", response_model=List[AIModelResponse])
async def list_ai_models(current_user: User = Depends(get_current_user)):
    return model_registry.list_models()


@router.get("/usage", response_model=AIUsageSummaryResponse)
async def get_ai_usage_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = str(current_user.id)
    stmt = select(
        func.count(AIUsage.id),
        func.coalesce(func.sum(AIUsage.total_tokens), 0),
        func.coalesce(func.sum(AIUsage.estimated_cost), 0.0),
        func.coalesce(func.sum(AIUsage.credits_used), 0),
    ).where(AIUsage.user_id == user_id)

    res = await db.execute(stmt)
    row = res.first()
    return AIUsageSummaryResponse(
        total_requests=row[0] or 0,
        total_tokens=row[1] or 0,
        total_estimated_cost=float(row[2] or 0.0),
        credits_used=row[3] or 0,
    )
