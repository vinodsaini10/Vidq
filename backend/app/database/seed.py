import asyncio
import logging
from sqlalchemy.future import select
from app.core.database import AsyncSessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models.enums import UserRole, UserStatus, SubscriptionStatus
from app.models.auth import User, UserProfile, Role, Permission
from app.models.billing import Plan, PlanFeature, Subscription
from app.models.youtube import YouTubeChannel, YouTubeVideo
from app.models.analytics import AnalyticsSnapshot
from app.models.keywords import Keyword
from app.models.competitors import Competitor
from app.models.admin import SystemSetting, FeatureFlag

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed")


async def seed_db():
    logger.info("Initializing Database Tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # Check if already seeded
        result = await session.execute(select(User).where(User.email == "admin@vidpulse.ai"))
        existing_admin = result.scalars().first()

        if existing_admin:
            logger.info("Database already seeded. Skipping.")
            return

        logger.info("Seeding Plans & Features...")
        plans_data = [
            {
                "name": "Free Creator",
                "code": "free",
                "price_monthly": 0.00,
                "price_yearly": 0.00,
                "ai_credits_monthly": 50,
                "max_channels": 1,
                "features": ["5 AI Script Generation/mo", "Basic Video SEO Score", "Community Support"]
            },
            {
                "name": "Starter Creator",
                "code": "starter",
                "price_monthly": 15.00,
                "price_yearly": 144.00,
                "ai_credits_monthly": 250,
                "max_channels": 2,
                "features": ["50 AI Scripts/mo", "CTR Prediction Engine", "Competitor Outlier Alerts"]
            },
            {
                "name": "Pro Creator",
                "code": "pro",
                "price_monthly": 29.00,
                "price_yearly": 276.00,
                "ai_credits_monthly": 1000,
                "max_channels": 5,
                "features": ["Unlimited AI Scripting", "Deep Research Gemini 3.6", "Priority Video Audit"]
            },
            {
                "name": "Business Studio",
                "code": "business",
                "price_monthly": 79.00,
                "price_yearly": 756.00,
                "ai_credits_monthly": 5000,
                "max_channels": 15,
                "features": ["Multi-user Team Seats", "Custom API Integrations", "Dedicated Account Manager"]
            },
            {
                "name": "Enterprise Scale",
                "code": "enterprise",
                "price_monthly": 199.00,
                "price_yearly": 1910.00,
                "ai_credits_monthly": 20000,
                "max_channels": 50,
                "features": ["Unlimited Team Access", "SLA Guarantees", "Custom AI Model Fine-tuning"]
            }
        ]

        created_plans = {}
        for p in plans_data:
            plan = Plan(
                name=p["name"],
                code=p["code"],
                price_monthly=p["price_monthly"],
                price_yearly=p["price_yearly"],
                currency="USD",
                ai_credits_monthly=p["ai_credits_monthly"],
                max_channels=p["max_channels"]
            )
            session.add(plan)
            await session.flush()
            created_plans[p["code"]] = plan

            for feat in p["features"]:
                pf = PlanFeature(
                    plan_id=plan.id,
                    feature_code=feat.lower().replace(" ", "_"),
                    feature_name=feat
                )
                session.add(pf)

        logger.info("Seeding Super Admin and Demo Users...")
        admin_user = User(
            email="admin@vidpulse.ai",
            hashed_password=get_password_hash("Admin123!SecurePass"),
            full_name="VidPulse Platform Admin",
            role=UserRole.SUPER_ADMIN,
            status=UserStatus.ACTIVE,
            is_active=True,
            is_verified=True,
            youtube_channel_title="VidPulse Official",
            youtube_handle="@vidpulse_official",
            youtube_subscriber_count=250000,
            ai_credits_max=10000,
            ai_credits_used=120
        )
        session.add(admin_user)
        await session.flush()

        admin_profile = UserProfile(
            user_id=admin_user.id,
            bio="Lead Platform Administrator for VidPulse AI SaaS",
            company="VidPulse Inc.",
            timezone="America/New_York"
        )
        session.add(admin_profile)

        demo_user = User(
            email="demo@vidpulse.ai",
            hashed_password=get_password_hash("DemoUser123!"),
            full_name="Alex Rivers",
            role=UserRole.PREMIUM_USER,
            status=UserStatus.ACTIVE,
            is_active=True,
            is_verified=True,
            youtube_channel_title="Alex Rivers Tech",
            youtube_handle="@alexriverstech",
            youtube_subscriber_count=124500,
            ai_credits_max=1000,
            ai_credits_used=85
        )
        session.add(demo_user)
        await session.flush()

        demo_subscription = Subscription(
            user_id=demo_user.id,
            plan_id=created_plans["pro"].id,
            status=SubscriptionStatus.ACTIVE,
            price=29.00,
            currency="USD"
        )
        session.add(demo_subscription)

        logger.info("Seeding Sample Channels & Videos...")
        channel = YouTubeChannel(
            user_id=demo_user.id,
            channel_id="UC_alex_rivers_tech_101",
            title="Alex Rivers Tech",
            description="Weekly deep dives on software engineering, AI tools, and SaaS architecture.",
            custom_url="https://youtube.com/@alexriverstech",
            subscriber_count=124500,
            video_count=84,
            view_count=12450000
        )
        session.add(channel)
        await session.flush()

        sample_video = YouTubeVideo(
            channel_id=channel.id,
            user_id=demo_user.id,
            video_id="v_gemini_saas_2026",
            title="I Built a Full Stack SaaS in 24 Hours with Gemini 3.6",
            status="Published",
            niche="AI & Tech SaaS",
            scheduled_date="2025-06-12",
            predicted_ctr="9.4%",
            estimated_views="150,000",
            seo_score=96,
            script_body="[HOOK]\nWhat if you could build a $10k/mo SaaS in 24 hours using AI?"
        )
        session.add(sample_video)

        logger.info("Seeding System Settings & Feature Flags...")
        sys_setting = SystemSetting(
            key="PLATFORM_MAINTENANCE_MODE",
            value="false",
            description="Global flag for API maintenance mode"
        )
        session.add(sys_setting)

        flag = FeatureFlag(
            key="enable_gemini_3_6_flash",
            name="Enable Gemini 3.6 Flash Generation Engine",
            is_enabled=True,
            rollout_percent="100"
        )
        session.add(flag)

        logger.info("Seeding Seed Keywords...")
        keywords_list = ["fastapi postgresql", "youtube seo growth", "gemini ai SaaS", "python 3.13 async"]
        for k in keywords_list:
            kw = Keyword(
                keyword=k,
                search_volume=74000,
                competition_score=0.35,
                opportunity_score=92
            )
            session.add(kw)

        await session.commit()
        logger.info("Database Seeding Completed Successfully! Demo Admin: admin@vidpulse.ai / Admin123!SecurePass")


if __name__ == "__main__":
    asyncio.run(seed_db())
