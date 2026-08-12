from app.core.celery_app import celery_app
from app.tasks import analytics_tasks  # register task modules

if __name__ == "__main__":
    celery_app.start()
