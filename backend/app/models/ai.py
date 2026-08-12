import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, ForeignKey, JSON, DateTime, Text, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import BaseModel
from app.models.enums import AIProvider, AIRequestStatus


class AIProviderModel(BaseModel):
    __tablename__ = "ai_provider_models"

    provider = Column(SQLEnum(AIProvider), default=AIProvider.GEMINI, nullable=False)
    model_name = Column(String, nullable=False, unique=True)  # gemini-3.6-flash, gpt-4o, llama3
    display_name = Column(String, nullable=True)
    context_window = Column(Integer, default=128000, nullable=False)
    input_price_per_1k = Column(Float, default=0.00015, nullable=False)
    output_price_per_1k = Column(Float, default=0.00060, nullable=False)
    max_tokens = Column(Integer, default=4096, nullable=False)
    temperature = Column(Float, default=0.7, nullable=False)
    capabilities = Column(JSON, default={
        "vision": True,
        "streaming": True,
        "embedding": False,
        "function_calling": True
    }, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)


class AIUsage(BaseModel):
    __tablename__ = "ai_usage"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    provider = Column(String, default="GEMINI", nullable=False)
    model_used = Column(String, default="gemini-3.6-flash", nullable=False)
    request_type = Column(String, nullable=False)  # title, script, seo, chat, thumbnail
    request_id = Column(String, nullable=True)
    prompt_tokens = Column(Integer, default=0, nullable=False)
    completion_tokens = Column(Integer, default=0, nullable=False)
    total_tokens = Column(Integer, default=0, nullable=False)
    estimated_cost = Column(Float, default=0.0, nullable=False)
    credits_used = Column(Integer, default=1, nullable=False)
    latency_ms = Column(Integer, default=0, nullable=False)
    status = Column(String, default="SUCCESS", nullable=False)
    error = Column(Text, nullable=True)


class AIRequest(BaseModel):
    __tablename__ = "ai_requests"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    prompt = Column(Text, nullable=False)
    type = Column(String, nullable=False)
    status = Column(SQLEnum(AIRequestStatus), default=AIRequestStatus.PENDING, nullable=False)

    response = relationship("AIResponse", back_populates="request", uselist=False, cascade="all, delete-orphan")


class AIResponse(BaseModel):
    __tablename__ = "ai_responses"

    request_id = Column(UUID(as_uuid=True), ForeignKey("ai_requests.id", ondelete="CASCADE"), unique=True, nullable=False)
    result_text = Column(Text, nullable=False)
    source = Column(String, default="gemini-3.6-flash", nullable=False)
    tokens_used = Column(Integer, default=150, nullable=False)

    request = relationship("AIRequest", back_populates="response")


class AIConversation(BaseModel):
    __tablename__ = "ai_conversations"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String, nullable=False)
    system_instruction = Column(Text, nullable=True)

    messages = relationship("AIMessage", back_populates="conversation", cascade="all, delete-orphan", order_by="AIMessage.created_at")


class AIMessage(BaseModel):
    __tablename__ = "ai_messages"

    conversation_id = Column(UUID(as_uuid=True), ForeignKey("ai_conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    sender = Column(String, nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    tokens_used = Column(Integer, default=0, nullable=False)
    feedback = Column(Integer, nullable=True)  # 1 for thumbs up, -1 for thumbs down

    conversation = relationship("AIConversation", back_populates="messages")


class AIPromptTemplate(BaseModel):
    __tablename__ = "ai_prompt_templates"

    name = Column(String, unique=True, nullable=False)
    category = Column(String, nullable=False)  # title, script, seo, chat, ideas
    description = Column(Text, nullable=True)
    system_prompt = Column(Text, nullable=False)
    user_prompt_template = Column(Text, nullable=False)
    variables = Column(JSON, default=[], nullable=False)
    version = Column(Integer, default=1, nullable=False)
    provider = Column(String, default="GEMINI", nullable=False)
    model = Column(String, default="gemini-3.6-flash", nullable=False)
    temperature = Column(Float, default=0.7, nullable=False)
    max_tokens = Column(Integer, default=2048, nullable=False)
    enabled = Column(Boolean, default=True, nullable=False)

    versions = relationship("AIPromptVersion", back_populates="template", cascade="all, delete-orphan")


class AIPromptVersion(BaseModel):
    __tablename__ = "ai_prompt_versions"

    template_id = Column(UUID(as_uuid=True), ForeignKey("ai_prompt_templates.id", ondelete="CASCADE"), nullable=False, index=True)
    version = Column(Integer, nullable=False)
    system_prompt = Column(Text, nullable=False)
    user_prompt_template = Column(Text, nullable=False)
    change_log = Column(Text, nullable=True)

    template = relationship("AIPromptTemplate", back_populates="versions")


class AIGeneratedContent(BaseModel):
    __tablename__ = "ai_generated_content"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content_type = Column(String, nullable=False)
    generated_text = Column(Text, nullable=False)


class AIGenerationHistory(BaseModel):
    __tablename__ = "ai_generation_history"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    prompt = Column(Text, nullable=False)
    output = Column(Text, nullable=False)
    feature = Column(String, default="general", nullable=False)
    model_used = Column(String, default="gemini-3.6-flash", nullable=False)
