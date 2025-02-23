from src.worker import celery_app
from src.core.db import engine
from sqlmodel import Session
from src.material.tfid.train import train_model
from src.core.config import settings
from sqlalchemy_file.storage import StorageManager


@celery_app.task(name='synchronize_documents_tasks')
def synchronize_documents_tasks():
    """Revectorize all materials."""
    
    with Session(engine) as session:
        train_model(db_session=session)

