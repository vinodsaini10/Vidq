from typing import List, Optional
from pydantic import BaseModel, Field


class TitleOption(BaseModel):
    title: str = Field(..., description="The generated YouTube video title")
    ctr_score: str = Field(..., description="Estimated CTR score percentage e.g. '95%'")
    type_category: str = Field(..., description="Category e.g. 'Curiosity Hook', 'Story Challenge', 'How-To'")
    reasoning: str = Field(..., description="Why this title works for YouTube algorithms")


class TitleResponse(BaseModel):
    titles: List[TitleOption]


class DescriptionResponse(BaseModel):
    seo_description: str
    summary_hook: str
    key_points: List[str]
    call_to_action: str
    hashtags: List[str]
    chapters: Optional[List[str]] = None


class TagItem(BaseModel):
    tag: str
    tag_type: str  # 'primary', 'secondary', 'long-tail'


class TagsResponse(BaseModel):
    primary_tags: List[str]
    secondary_tags: List[str]
    long_tail_tags: List[str]
    formatted_comma_separated: str


class HookItem(BaseModel):
    angle: str  # Curiosity, Shock, Question, Story, Problem, Contrarian, Emotional
    hook_text: str
    why_it_works: str


class HooksResponse(BaseModel):
    hooks: List[HookItem]


class ScriptSection(BaseModel):
    section_title: str
    timestamp: str
    visual_cue: str
    audio_narration: str


class ScriptResponse(BaseModel):
    title: str
    format: str  # Shorts, 1m, 3m, 5m, 10m, Long-form
    hook: str
    intro: str
    sections: List[ScriptSection]
    outro_cta: str


class IdeaItem(BaseModel):
    title: str
    angle: str
    target_audience: str
    ctr_potential: str
    thumbnail_concept: str


class ContentIdeasResponse(BaseModel):
    ideas: List[IdeaItem]


class SEOIssue(BaseModel):
    severity: str  # High, Medium, Low
    issue: str
    recommendation: str


class SEOAnalysisResponse(BaseModel):
    seo_score: int
    strengths: List[str]
    issues: List[SEOIssue]
    recommended_keywords: List[str]
    optimized_title_suggestion: str


class ThumbnailPromptOption(BaseModel):
    concept_title: str
    midjourney_prompt: str
    visual_elements: str
    color_palette: str
    text_overlay: str


class ThumbnailPromptResponse(BaseModel):
    concepts: List[ThumbnailPromptOption]


class CompetitorAnalysisResponse(BaseModel):
    top_performing_topics: List[str]
    content_gaps: List[str]
    upload_patterns: str
    recommendations: List[str]


class ChannelCoachResponse(BaseModel):
    summary: str
    strengths: List[str]
    growth_bottlenecks: List[str]
    action_steps: List[str]
    recommended_next_video: str
