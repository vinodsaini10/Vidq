from pydantic import BaseModel
from typing import List, Dict, Any


class AnalyticsOverview(BaseModel):
    total_views: int
    subscribers: int
    estimated_revenue: float
    avg_ctr: float
    channel_health_score: int
    monthly_impressions: int
    historical_chart_data: List[Dict[str, Any]]
