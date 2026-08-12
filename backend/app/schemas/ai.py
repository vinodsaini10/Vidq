from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class AIGenerateRequest(BaseModel):
    prompt: str
    type: str  # title, script, seo, description, tags, thumbnail, competitor
    parameters: Optional[Dict[str, Any]] = None


class AIGenerateResponse(BaseModel):
    result: Any
    source: str
    tokens_used: int = 150


class AIChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str
    model: Optional[str] = None


class AIConversationCreateRequest(BaseModel):
    title: Optional[str] = "New Chat"
    system_instruction: Optional[str] = None


class AIConversationRenameRequest(BaseModel):
    title: str


class AIMessageFeedbackRequest(BaseModel):
    message_id: str
    feedback: int  # 1 for thumbs up, -1 for thumbs down


class AIMessageResponse(BaseModel):
    id: str
    conversation_id: str
    sender: str
    content: str
    tokens_used: int
    feedback: Optional[int] = None
    created_at: datetime


class AIConversationResponse(BaseModel):
    id: str
    title: str
    system_instruction: Optional[str] = None
    created_at: datetime
    messages: Optional[List[AIMessageResponse]] = []


class AITitleGenerateRequest(BaseModel):
    topic: str
    audience: Optional[str] = "General"
    tone: Optional[str] = "Engaging & Viral"
    provider: Optional[str] = None
    model: Optional[str] = None


class AIDescriptionGenerateRequest(BaseModel):
    topic: str
    key_points: Optional[str] = ""
    cta: Optional[str] = "Subscribe for more videos!"


class AITagsGenerateRequest(BaseModel):
    topic: str
    keywords: Optional[str] = ""


class AIHooksGenerateRequest(BaseModel):
    topic: str
    audience: Optional[str] = "General"


class AIScriptGenerateRequest(BaseModel):
    topic: str
    format: Optional[str] = "5 minute"
    tone: Optional[str] = "Engaging & Informative"


class AIIdeasGenerateRequest(BaseModel):
    niche: str
    audience: Optional[str] = "General"


class AIThumbnailPromptRequest(BaseModel):
    topic: str
    emotion: Optional[str] = "Shocked / High Contrast"


class AISEOAnalysisRequest(BaseModel):
    title: str
    description: Optional[str] = ""
    tags: Optional[str] = ""
    keywords: Optional[str] = ""


class AICompetitorAnalysisRequest(BaseModel):
    my_topic: str


class AIChannelCoachRequest(BaseModel):
    question: str


class AICreditsResponse(BaseModel):
    user_id: str
    credits_max: int
    credits_used: int
    credits_remaining: int
    role: str


class AIModelResponse(BaseModel):
    model_name: str
    provider: str
    display_name: str
    context_window: int
    input_price_per_1k: float
    output_price_per_1k: float
    max_tokens: int
    temperature: float
    capabilities: Dict[str, Any]
    is_active: bool
    is_default: bool


class AIUsageSummaryResponse(BaseModel):
    total_requests: int
    total_tokens: int
    total_estimated_cost: float
    credits_used: int
