# ============================================================
# Celery Application Configuration
# File: app/tasks/celery_app.py
# ============================================================

from celery import Celery

from app.config import get_settings

settings = get_settings()

# Create Celery application
celery_app = Celery(
    "callagent",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

# Celery configuration
celery_app.conf.update(
    # Serialization
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],

    # Timezone
    timezone="UTC",
    enable_utc=True,

    # Task routing — different queues for different task types
    task_routes={
        "app.tasks.call_tasks.*": {"queue": "calls"},
        "app.tasks.batch_tasks.*": {"queue": "default"},
        "app.tasks.report_tasks.*": {"queue": "reports"},
    },

    # Retry settings
    task_acks_late=True,
    worker_prefetch_multiplier=1,

    # Result expiry (24 hours)
    result_expires=86400,

    # Concurrency
    worker_concurrency=10,

    # Rate limiting
    task_default_rate_limit="30/m",  # Max 30 tasks per minute by default

    # Task time limits
    task_soft_time_limit=600,   # 10 minutes soft limit
    task_time_limit=900,        # 15 minutes hard limit
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["app.tasks"])
