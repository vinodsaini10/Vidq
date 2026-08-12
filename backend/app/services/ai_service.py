import json
import logging
from google import genai
from app.core.config import settings

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self):
        self.client = None
        if settings.GEMINI_API_KEY:
            try:
                self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini Client: {e}")

    async def generate_content(self, prompt: str, type_str: str, parameters: dict = None) -> dict:
        system_prompts = {
            "title": "You are a master YouTube title strategist. Generate 5 viral title options with CTR predictions and power word analysis.",
            "script": "You are a top 1% YouTube scriptwriter. Write structured video scripts with Hooks, Intros, Main Visual Cues, CTAs, and Timestamps.",
            "seo": "You are a YouTube SEO Specialist. Analyze the title/topic and provide an SEO Score (0-100), key recommendation points, and target tags.",
            "description": "Generate a high-converting, SEO optimized YouTube description with chapters, summary, and call to action.",
            "tags": "Generate 20 high-volume, relevant YouTube tags separated by commas.",
            "thumbnail": "Generate 3 visual Midjourney / Flux image prompts for YouTube thumbnails.",
            "competitor": "Analyze competitor videos in this niche and identify outlier topics and content gaps."
        }

        instruction = system_prompts.get(type_str, "You are an expert YouTube growth AI assistant.")

        if not self.client:
            return {
                "result": self._get_simulated_ai_response(type_str, prompt),
                "source": "simulated"
            }

        try:
            response = self.client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
                config={
                    "system_instruction": instruction,
                    "temperature": 0.7,
                }
            )
            return {
                "result": response.text,
                "source": "gemini-3.6-flash"
            }
        except Exception as e:
            logger.error(f"Gemini API generation error: {e}")
            return {
                "result": self._get_simulated_ai_response(type_str, prompt),
                "source": "fallback_simulated"
            }

    def _get_simulated_ai_response(self, type_str: str, prompt: str) -> str:
        topic = prompt[:40] if len(prompt) > 40 else prompt

        if type_str == "title":
            return json.dumps([
                {"title": f"I Tested {topic} For 30 Days (SHOCKING Results)", "ctrScore": "96%", "type": "Story / Challenge"},
                {"title": f"Why 99% of Creators Fail at {topic} (And How to Fix It)", "ctrScore": "94%", "type": "Curiosity / Fear"},
                {"title": f"The Ultimate {topic} Blueprint for 2026 [Step-by-Step]", "ctrScore": "91%", "type": "How-To / Value"},
                {"title": f"Stop Doing {topic} Like This! (Do This Instead)", "ctrScore": "89%", "type": "Negative Framing"},
                {"title": f"How I Scaled {topic} to $10,000/Mo Without Showing My Face", "ctrScore": "95%", "type": "Financial / Proof"}
            ], indent=2)

        if type_str == "seo":
            return json.dumps({
                "overallScore": 88,
                "strengths": ["Strong emotional hook", "Primary keyword near front", "High search interest"],
                "improvements": ["Add timestamps", "Add 2 links above fold"],
                "recommendedTags": [f"{topic} tutorial", f"best {topic} 2026", "youtube growth", "viral tips"]
            }, indent=2)

        return f"[VidPulse AI Engine] Detailed growth breakdown generated for topic: '{topic}' with 90%+ viral score prediction."


ai_service = AIService()
