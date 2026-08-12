import logging
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.ai import AIPromptTemplate, AIPromptVersion
from app.services.ai.safety import safety_layer

logger = logging.getLogger(__name__)


DEFAULT_TEMPLATES = {
    "title_generator": {
        "category": "title",
        "description": "Generates 10 high-CTR YouTube titles categorized by psychological hooks.",
        "system_prompt": "You are a world-class YouTube title strategist and growth hacker. Generate high-CTR titles designed for max engagement, curiosity, and search relevance.",
        "user_prompt_template": "Topic/Keyword: {topic}\nTarget Audience: {audience}\nTone: {tone}\nChannel Context: {context}\n\nGenerate 10 viral YouTube title variations with CTR predictions and psychological reasoning.",
        "variables": ["topic", "audience", "tone", "context"],
    },
    "title_optimizer": {
        "category": "title",
        "description": "Optimizes an existing title for maximum CTR and SEO.",
        "system_prompt": "You are a YouTube CTR and title optimization specialist.",
        "user_prompt_template": "Current Title: {current_title}\nCategory/Niche: {niche}\nTarget Keyword: {keyword}\n\nAnalyze why the title underperforms and provide 5 optimized title options with CTR uplift scores.",
        "variables": ["current_title", "niche", "keyword"],
    },
    "description_generator": {
        "category": "description",
        "description": "Generates high-converting, SEO-optimized YouTube descriptions.",
        "system_prompt": "You are a YouTube SEO copywriter. Generate structured, engaging video descriptions with timestamps, CTAs, and hashtags.",
        "user_prompt_template": "Video Topic: {topic}\nKey Points: {key_points}\nLinks/CTA: {cta}\n\nWrite an engaging 300+ word YouTube description with intro hook, timestamp placeholders, call to action, and 5 hashtags.",
        "variables": ["topic", "key_points", "cta"],
    },
    "tags_generator": {
        "category": "tags",
        "description": "Generates primary, secondary, and long-tail tags.",
        "system_prompt": "You are a YouTube Tag & Metadata strategist. Produce comma-separated relevant tags.",
        "user_prompt_template": "Video Title/Topic: {topic}\nKeywords: {keywords}\n\nGenerate 20 high-performing YouTube tags broken down into primary, secondary, and long-tail tags.",
        "variables": ["topic", "keywords"],
    },
    "hook_generator": {
        "category": "script",
        "description": "Generates 7 psychological hook categories for video intros.",
        "system_prompt": "You are a YouTube retention specialist. Generate killer 5-second video hooks across curiosity, shock, question, story, problem, contrarian, and emotional angles.",
        "user_prompt_template": "Topic: {topic}\nTarget Audience: {audience}\n\nGenerate 7 distinct retention hooks for the first 5 seconds of the video.",
        "variables": ["topic", "audience"],
    },
    "script_generator": {
        "category": "script",
        "description": "Generates full structured video scripts.",
        "system_prompt": "You are a master YouTube scriptwriter. Structure scripts with visual cues, retention triggers, voiceover text, timestamps, and CTAs.",
        "user_prompt_template": "Topic: {topic}\nFormat: {format}\nTarget Duration: {duration}\nTone: {tone}\nChannel Context: {context}\n\nWrite a complete production-ready script with Hook, Intro, Core Sections, Visual Directions, Transition Cues, and Outro CTA.",
        "variables": ["topic", "format", "duration", "tone", "context"],
    },
    "ideas_generator": {
        "category": "ideas",
        "description": "Generates actionable viral video ideas based on channel niche.",
        "system_prompt": "You are a YouTube content director. Brainstorm viral video ideas with high audience demand.",
        "user_prompt_template": "Channel Niche: {niche}\nTarget Audience: {audience}\nChannel Performance Context: {context}\n\nGenerate 10 high-potential video ideas with titles, core hooks, and thumbnail concepts.",
        "variables": ["niche", "audience", "context"],
    },
    "seo_analyzer": {
        "category": "seo",
        "description": "Analyzes video metadata for SEO scores and recommendations.",
        "system_prompt": "You are a YouTube SEO Audit Expert.",
        "user_prompt_template": "Title: {title}\nDescription: {description}\nTags: {tags}\nKeywords: {keywords}\n\nAnalyze the metadata, compute an SEO score (0-100), list critical issues, and provide prioritized action steps.",
        "variables": ["title", "description", "tags", "keywords"],
    },
    "thumbnail_prompt": {
        "category": "thumbnail",
        "description": "Generates visual AI image prompts for Flux / Midjourney YouTube thumbnails.",
        "system_prompt": "You are an expert YouTube Thumbnail Art Director.",
        "user_prompt_template": "Video Topic/Title: {topic}\nVisual Vibe/Emotion: {emotion}\n\nGenerate 3 detailed Midjourney/Flux image generation prompts specifying Subject, Expression, Lighting, Composition, Color Palette, and Text Overlay Placement.",
        "variables": ["topic", "emotion"],
    },
    "competitor_analyzer": {
        "category": "competitor",
        "description": "Analyzes competitor video titles and topic gaps.",
        "system_prompt": "You are a YouTube Competitive Intelligence Analyst.",
        "user_prompt_template": "Competitor Channel/Videos Data:\n{competitor_data}\nMy Channel Topic: {my_topic}\n\nIdentify top performing content themes, outlier video topics, and 5 unfulfilled content gaps my channel can capture.",
        "variables": ["competitor_data", "my_topic"],
    },
    "channel_coach": {
        "category": "coach",
        "description": "AI Growth Coach giving personalized recommendations based on actual channel performance.",
        "system_prompt": "You are a elite YouTube Channel Growth Coach and Strategist.",
        "user_prompt_template": "User Channel Analytics & Performance Context:\n{context}\nUser Question: {question}\n\nProvide clear, data-driven advice with actionable next steps.",
        "variables": ["context", "question"],
    }
}


class PromptEngine:
    """Centralized prompt template management, versioning, rendering, and rollbacks."""

    async def get_or_create_template(
        self, db: AsyncSession, name: str
    ) -> AIPromptTemplate:
        stmt = select(AIPromptTemplate).where(AIPromptTemplate.name == name)
        res = await db.execute(stmt)
        template = res.scalars().first()

        if not template:
            default_info = DEFAULT_TEMPLATES.get(name, {
                "category": "general",
                "description": f"Default template for {name}",
                "system_prompt": "You are an expert YouTube AI Assistant.",
                "user_prompt_template": "Topic: {topic}\n\nAnalyze and generate growth output.",
                "variables": ["topic"]
            })

            template = AIPromptTemplate(
                name=name,
                category=default_info["category"],
                description=default_info.get("description", ""),
                system_prompt=default_info["system_prompt"],
                user_prompt_template=default_info["user_prompt_template"],
                variables=default_info.get("variables", []),
                version=1,
                enabled=True,
            )
            db.add(template)
            await db.commit()
            await db.refresh(template)

        return template

    def render_prompt(
        self, template: AIPromptTemplate, variables: Dict[str, Any]
    ) -> tuple[str, str]:
        """Renders system prompt and user prompt safely with variable substitution."""
        system_prompt = template.system_prompt

        user_template = template.user_prompt_template
        # Substitute variables safely
        rendered_user = user_template
        for key, val in variables.items():
            str_val = safety_layer.sanitize_external_content(str(val) if val is not None else "")
            rendered_user = rendered_user.replace(f"{{{key}}}", str_val)

        return system_prompt, rendered_user

    async def create_new_version(
        self,
        db: AsyncSession,
        template_id: str,
        new_system_prompt: str,
        new_user_prompt: str,
        change_log: str = "Updated prompt version"
    ) -> AIPromptTemplate:
        stmt = select(AIPromptTemplate).where(AIPromptTemplate.id == template_id)
        res = await db.execute(stmt)
        template = res.scalars().first()

        if not template:
            raise ValueError("Prompt template not found.")

        # Save previous version to history
        version_history = AIPromptVersion(
            template_id=template.id,
            version=template.version,
            system_prompt=template.system_prompt,
            user_prompt_template=template.user_prompt_template,
            change_log=change_log
        )
        db.add(version_history)

        # Update active template
        template.version += 1
        template.system_prompt = new_system_prompt
        template.user_prompt_template = new_user_prompt

        await db.commit()
        await db.refresh(template)
        return template


prompt_engine = PromptEngine()
