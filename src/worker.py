from celery import Celery
from src.core.config import settings

celery_app = Celery(__name__, include=["src.worker", "src.users.tasks"])
celery_app.conf.broker_url = settings.CELERY_BROKER_URL
celery_app.conf.result_backend = settings.CELERY_RESULT_BACKEND
