from celery import Celery, Task
from src.core.config import settings
from src.libs.log import logger
from sqlalchemy_file.storage import StorageManager
from celery.signals import task_postrun, task_prerun

celery_app = Celery(__name__, include=["src.worker", "src.users.tasks", "src.admin.tasks", 'src.material.tasks'])
celery_app.conf.broker_url = settings.CELERY_BROKER_URL
celery_app.conf.result_backend = settings.CELERY_RESULT_BACKEND

if settings.file_storage_container:
    try:
        StorageManager.add_storage(
            settings.FILE_STORAGE_CONTAINER_NAME, settings.file_storage_container
        )
    except RuntimeError:
        pass


@task_prerun.connect
def _log_task_before_run(task_id: str, task: Task, *args, **kwargs) -> None:  # type: ignore  # noqa
    """Log task before it runs."""
    logger.info(f"Stating task: {task.name}")


@task_postrun.connect
def _log_task_after_run(task_id: str, task: Task, *args, **kwargs) -> None:  # type: ignore  # noqa
    """Log task after it runs."""
    logger.info(f"Task {task.name} finished")
