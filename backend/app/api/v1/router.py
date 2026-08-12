from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    users,
    dashboard,
    analytics,
    keywords,
    seo,
    videos,
    competitors,
    reports,
    ai,
    notifications,
    billing,
    admin,
    admin_billing,
    webhooks,
    settings as settings_ep,
    support,
    youtube,
    health,
)

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["Health Checks"])
api_router.include_router(youtube.router, prefix="/youtube", tags=["YouTube API"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(keywords.router, prefix="/keywords", tags=["Keywords"])
api_router.include_router(seo.router, prefix="/seo", tags=["Video SEO"])
api_router.include_router(videos.router, prefix="/videos", tags=["Videos"])
api_router.include_router(competitors.router, prefix="/competitors", tags=["Competitors"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI Generation"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(billing.router, prefix="/billing", tags=["Billing"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(admin_billing.router, prefix="/admin/billing", tags=["Admin Billing"])
api_router.include_router(settings_ep.router, prefix="/settings", tags=["Settings"])
api_router.include_router(support.router, prefix="/support", tags=["Support"])
