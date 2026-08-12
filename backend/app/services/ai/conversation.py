import logging
from typing import List, Optional, Dict, Any, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from fastapi import HTTPException

from app.models.ai import AIConversation, AIMessage
from app.services.ai.gateway import ai_gateway
from app.services.ai.prompt_engine import prompt_engine

logger = logging.getLogger(__name__)


class AIConversationManager:
    """Manages AI Chat Conversations, Messages, History, and Streaming Responses."""

    async def create_conversation(
        self, db: AsyncSession, user_id: str, title: str = "New Chat", system_instruction: Optional[str] = None
    ) -> AIConversation:
        conversation = AIConversation(
            user_id=user_id,
            title=title,
            system_instruction=system_instruction or "You are an expert YouTube growth AI assistant.",
        )
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
        return conversation

    async def list_conversations(self, db: AsyncSession, user_id: str) -> List[AIConversation]:
        stmt = (
            select(AIConversation)
            .where(AIConversation.user_id == user_id)
            .order_by(AIConversation.created_at.desc())
        )
        res = await db.execute(stmt)
        return list(res.scalars().all())

    async def get_conversation(
        self, db: AsyncSession, user_id: str, conversation_id: str
    ) -> AIConversation:
        stmt = select(AIConversation).where(
            AIConversation.id == conversation_id, AIConversation.user_id == user_id
        )
        res = await db.execute(stmt)
        conv = res.scalars().first()
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found.")
        return conv

    async def rename_conversation(
        self, db: AsyncSession, user_id: str, conversation_id: str, new_title: str
    ) -> AIConversation:
        conv = await self.get_conversation(db, user_id, conversation_id)
        conv.title = new_title
        await db.commit()
        await db.refresh(conv)
        return conv

    async def delete_conversation(self, db: AsyncSession, user_id: str, conversation_id: str) -> bool:
        conv = await self.get_conversation(db, user_id, conversation_id)
        await db.delete(conv)
        await db.commit()
        return True

    async def send_message(
        self,
        db: AsyncSession,
        user_id: str,
        conversation_id: str,
        user_content: str,
        model_name: Optional[str] = None,
    ) -> AIMessage:
        conv = await self.get_conversation(db, user_id, conversation_id)

        # 1. Save user message
        user_msg = AIMessage(
            conversation_id=conv.id,
            sender="user",
            content=user_content,
        )
        db.add(user_msg)
        await db.commit()

        # 2. Build dialogue context history
        stmt_msgs = (
            select(AIMessage)
            .where(AIMessage.conversation_id == conv.id)
            .order_by(AIMessage.created_at.asc())
            .limit(10)
        )
        res_msgs = await db.execute(stmt_msgs)
        past_msgs = res_msgs.scalars().all()

        history_str = "\n".join([f"{m.sender.upper()}: {m.content}" for m in past_msgs])
        system_instruction = conv.system_instruction or "You are an expert YouTube growth coach."

        # 3. Call AI Gateway
        ai_resp = await ai_gateway.generate(
            db=db,
            user_id=user_id,
            feature="chat",
            prompt=f"Dialogue History:\n{history_str}\n\nASSISTANT:",
            system_prompt=system_instruction,
            model_name=model_name,
            credits_cost=1,
        )

        # 4. Save Assistant response message
        assistant_msg = AIMessage(
            conversation_id=conv.id,
            sender="assistant",
            content=ai_resp.text,
            tokens_used=ai_resp.total_tokens,
        )
        db.add(assistant_msg)

        # Auto-update conversation title if default "New Chat"
        if conv.title == "New Chat":
            conv.title = user_content[:30] + ("..." if len(user_content) > 30 else "")

        await db.commit()
        await db.refresh(assistant_msg)
        return assistant_msg

    async def update_message_feedback(
        self, db: AsyncSession, user_id: str, message_id: str, feedback: int
    ) -> AIMessage:
        stmt = select(AIMessage).where(AIMessage.id == message_id)
        res = await db.execute(stmt)
        msg = res.scalars().first()
        if not msg:
            raise HTTPException(status_code=404, detail="Message not found.")

        msg.feedback = feedback
        await db.commit()
        await db.refresh(msg)
        return msg


conversation_manager = AIConversationManager()
