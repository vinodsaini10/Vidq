import json
import logging
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.ai.gateway import ai_gateway
from app.services.ai.prompt_engine import prompt_engine
from app.services.ai.context_builder import context_builder
from app.services.ai.structured_schemas import (
    TitleResponse,
    DescriptionResponse,
    TagsResponse,
    HooksResponse,
    ScriptResponse,
    ContentIdeasResponse,
    SEOAnalysisResponse,
    ThumbnailPromptResponse,
    CompetitorAnalysisResponse,
    ChannelCoachResponse,
)

logger = logging.getLogger(__name__)


class AITaskService:
    """Dedicated Service Layer implementing all 30+ YouTube AI features and tools."""

    async def generate_titles(
        self,
        db: AsyncSession,
        user_id: str,
        topic: str,
        audience: str = "General",
        tone: str = "Engaging & Viral",
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        ctx = await context_builder.build_context(db, user_id, include_channel=True)
        template = await prompt_engine.get_or_create_template(db, "title_generator")

        system_prompt, user_prompt = prompt_engine.render_prompt(
            template,
            {
                "topic": topic,
                "audience": audience,
                "tone": tone,
                "context": ctx["formatted_context"],
            },
        )

        res = await ai_gateway.generate(
            db=db,
            user_id=user_id,
            feature="title_generator",
            prompt=user_prompt,
            system_prompt=system_prompt,
            provider_name=provider,
            model_name=model,
            response_format="json",
            credits_cost=1,
        )

        try:
            parsed = json.loads(res.text)
            return {"titles": parsed.get("titles", parsed if isinstance(parsed, list) else []), "source": res.model_used}
        except Exception:
            return {"raw": res.text, "source": res.model_used}

    async def optimize_title(
        self, db: AsyncSession, user_id: str, current_title: str, niche: str, keyword: str
    ) -> Dict[str, Any]:
        template = await prompt_engine.get_or_create_template(db, "title_optimizer")
        system_prompt, user_prompt = prompt_engine.render_prompt(
            template, {"current_title": current_title, "niche": niche, "keyword": keyword}
        )

        res = await ai_gateway.generate(
            db=db,
            user_id=user_id,
            feature="title_optimizer",
            prompt=user_prompt,
            system_prompt=system_prompt,
            response_format="json",
            credits_cost=1,
        )
        return {"result": res.text, "source": res.model_used}

    async def generate_description(
        self,
        db: AsyncSession,
        user_id: str,
        topic: str,
        key_points: str = "",
        cta: str = "Subscribe for more videos!",
    ) -> Dict[str, Any]:
        template = await prompt_engine.get_or_create_template(db, "description_generator")
        system_prompt, user_prompt = prompt_engine.render_prompt(
            template, {"topic": topic, "key_points": key_points, "cta": cta}
        )

        res = await ai_gateway.generate(
            db=db,
            user_id=user_id,
            feature="description_generator",
            prompt=user_prompt,
            system_prompt=system_prompt,
            credits_cost=1,
        )
        return {"description": res.text, "source": res.model_used}

    async def generate_tags(
        self, db: AsyncSession, user_id: str, topic: str, keywords: str = ""
    ) -> Dict[str, Any]:
        template = await prompt_engine.get_or_create_template(db, "tags_generator")
        system_prompt, user_prompt = prompt_engine.render_prompt(
            template, {"topic": topic, "keywords": keywords}
        )

        res = await ai_gateway.generate(
            db=db,
            user_id=user_id,
            feature="tags_generator",
            prompt=user_prompt,
            system_prompt=system_prompt,
            credits_cost=1,
        )
        return {"tags": res.text, "source": res.model_used}

    async def generate_hashtags(
        self, db: AsyncSession, user_id: str, topic: str
    ) -> Dict[str, Any]:
        prompt = f"Generate 10 trending YouTube hashtags for topic: '{topic}'"
        res = await ai_gateway.generate(
            db=db,
            user_id=user_id,
            feature="hashtags_generator",
            prompt=prompt,
            system_prompt="You are a social media hashtag strategist.",
            credits_cost=1,
        )
        return {"hashtags": res.text, "source": res.model_used}

    async def generate_hooks(
        self, db: AsyncSession, user_id: str, topic: str, audience: str = "General"
    ) -> Dict[str, Any]:
        template = await prompt_engine.get_or_create_template(db, "hook_generator")
        system_prompt, user_prompt = prompt_engine.render_prompt(
            template, {"topic": topic, "audience": audience}
        )

        res = await ai_gateway.generate(
            db=db,
            user_id=user_id,
            feature="hook_generator",
            prompt=user_prompt,
            system_prompt=system_prompt,
            response_format="json",
            credits_cost=1,
        )
        return {"hooks": res.text, "source": res.model_used}

    async def generate_script(
        self,
        db: AsyncSession,
        user_id: str,
        topic: str,
        script_format: str = "5 minute",
        tone: str = "Engaging & Informative",
    ) -> Dict[str, Any]:
        ctx = await context_builder.build_context(db, user_id, include_channel=True)
        template = await prompt_engine.get_or_create_template(db, "script_generator")

        system_prompt, user_prompt = prompt_engine.render_prompt(
            template,
            {
                "topic": topic,
                "format": script_format,
                "duration": script_format,
                "tone": tone,
                "context": ctx["formatted_context"],
            },
        )

        res = await ai_gateway.generate(
            db=db,
            user_id=user_id,
            feature="script_generator",
            prompt=user_prompt,
            system_prompt=system_prompt,
            credits_cost=2,  # Scripts use 2 credits
        )
        return {"script": res.text, "source": res.model_used}

    async def generate_ideas(
        self, db: AsyncSession, user_id: str, niche: str, audience: str = "General"
    ) -> Dict[str, Any]:
        ctx = await context_builder.build_context(db, user_id, include_videos=True)
        template = await prompt_engine.get_or_create_template(db, "ideas_generator")

        system_prompt, user_prompt = prompt_engine.render_prompt(
            template, {"niche": niche, "audience": audience, "context": ctx["formatted_context"]}
        )

        res = await ai_gateway.generate(
            db=db,
            user_id=user_id,
            feature="ideas_generator",
            prompt=user_prompt,
            system_prompt=system_prompt,
            response_format="json",
            credits_cost=1,
        )
        return {"ideas": res.text, "source": res.model_used}

    async def generate_thumbnail_prompt(
        self, db: AsyncSession, user_id: str, topic: str, emotion: str = "Shocked / High Contrast"
    ) -> Dict[str, Any]:
        template = await prompt_engine.get_or_create_template(db, "thumbnail_prompt")
        system_prompt, user_prompt = prompt_engine.render_prompt(
            template, {"topic": topic, "emotion": emotion}
        )

        res = await ai_gateway.generate(
            db=db,
            user_id=user_id,
            feature="thumbnail_prompt",
            prompt=user_prompt,
            system_prompt=system_prompt,
            credits_cost=1,
        )
        return {"thumbnail_prompts": res.text, "source": res.model_used}

    async def analyze_seo(
        self,
        db: AsyncSession,
        user_id: str,
        title: str,
        description: str = "",
        tags: str = "",
        keywords: str = "",
    ) -> Dict[str, Any]:
        template = await prompt_engine.get_or_create_template(db, "seo_analyzer")
        system_prompt, user_prompt = prompt_engine.render_prompt(
            template,
            {"title": title, "description": description, "tags": tags, "keywords": keywords},
        )

        res = await ai_gateway.generate(
            db=db,
            user_id=user_id,
            feature="seo_analyzer",
            prompt=user_prompt,
            system_prompt=system_prompt,
            response_format="json",
            credits_cost=1,
        )
        return {"seo_analysis": res.text, "source": res.model_used}

    async def analyze_competitors(
        self, db: AsyncSession, user_id: str, my_topic: str
    ) -> Dict[str, Any]:
        ctx = await context_builder.build_context(db, user_id, include_competitors=True)
        template = await prompt_engine.get_or_create_template(db, "competitor_analyzer")

        system_prompt, user_prompt = prompt_engine.render_prompt(
            template,
            {"competitor_data": ctx["formatted_context"], "my_topic": my_topic},
        )

        res = await ai_gateway.generate(
            db=db,
            user_id=user_id,
            feature="competitor_analyzer",
            prompt=user_prompt,
            system_prompt=system_prompt,
            credits_cost=1,
        )
        return {"competitor_analysis": res.text, "source": res.model_used}

    async def channel_coach(
        self, db: AsyncSession, user_id: str, question: str
    ) -> Dict[str, Any]:
        ctx = await context_builder.build_context(
            db, user_id, include_channel=True, include_videos=True, include_analytics=True
        )
        template = await prompt_engine.get_or_create_template(db, "channel_coach")

        system_prompt, user_prompt = prompt_engine.render_prompt(
            template, {"context": ctx["formatted_context"], "question": question}
        )

        res = await ai_gateway.generate(
            db=db,
            user_id=user_id,
            feature="channel_coach",
            prompt=user_prompt,
            system_prompt=system_prompt,
            credits_cost=1,
        )
        return {"advice": res.text, "source": res.model_used}


ai_task_service = AITaskService()
