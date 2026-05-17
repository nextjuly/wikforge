"""Celery application configuration.

Configures the Celery app used by the document processing pipeline and other
asynchronous workloads:

- Broker / result backend: Redis (derived from REDIS_* settings via
  ``settings.celery_broker_url`` / ``settings.celery_result_backend``).
- Task discovery: tasks under ``app.tasks`` are loaded via the constructor
  ``include`` argument and an explicit ``autodiscover_tasks`` call so that
  tasks are registered both when running ``celery worker`` and when the app
  is imported by FastAPI.
- Retry policy: exponential backoff with jitter, ``acks_late`` so messages
  are not lost on worker crashes, and a hard 60s per-task time limit
  matching the "single step 60s" design constraint.
"""

from celery import Celery

from app.core.config import get_settings

settings = get_settings()

# Modules containing @shared_task / @celery_app.task definitions. Listed
# explicitly so the worker can register tasks without relying solely on
# autodiscovery (which only runs after ``finalize`` and can miss imports
# under some entrypoints).
TASK_MODULES = [
    "app.tasks.pipeline",
    "app.tasks.permission_tasks",
]

celery_app = Celery(
    "wikforge",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=TASK_MODULES,
)

# Also run autodiscover so any future module added under ``app.tasks`` is
# picked up without having to update ``TASK_MODULES``.
celery_app.autodiscover_tasks(["app.tasks"])

# Celery configuration
celery_app.conf.update(
    # --- Serialization ---
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # --- Reliability / acknowledgement ---
    # acks_late ensures a task is only acknowledged after successful execution,
    # so a worker crash mid-task causes the broker to redeliver it.
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_track_started=True,
    worker_prefetch_multiplier=1,
    # --- Retry policy (exponential backoff with jitter) ---
    task_default_retry_delay=10,  # initial delay between retries (seconds)
    task_max_retries=3,
    task_retry_backoff=True,
    task_retry_backoff_max=600,  # cap exponential backoff at 10 minutes
    task_retry_jitter=True,
    # --- Time limits (matches design: per-step 60s timeout) ---
    task_soft_time_limit=50,  # raises SoftTimeLimitExceeded for graceful cleanup
    task_time_limit=60,  # hard kill after 60s
    # --- Result backend ---
    result_expires=3600,  # results expire after 1 hour
    # --- Worker resource hygiene ---
    worker_max_tasks_per_child=100,
    worker_max_memory_per_child=512_000,  # 512MB
)
