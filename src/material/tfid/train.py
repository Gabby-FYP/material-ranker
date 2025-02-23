from sqlmodel import Session, select, col, update, delete
from src.models import Material, MaterialStatus
from src.material.parsers.text import Parser as TextParser
from src.material.tfid.vertorizer import Vectorizer
from src.core.config import settings
import io


def train_model(db_session: Session) -> None:
    """Vectoriize TFIDF model."""
    
    materials = db_session.exec(
        select(Material).where(
            col(Material.status).in_([
                MaterialStatus.pending_vectorization, 
                MaterialStatus.vectorized
            ])
        ).order_by(col(Material.vector_id))
    ).all()
    
    documents = [
        TextParser(
            io.BytesIO(material.content.file.read())
        ).parse() for material in materials
    ]

    if documents:
        Vectorizer().train(documents)

        # mark all pending vectorization materials as vectorized
        db_session.exec(
            update(Material).where(
                col(Material.status) == MaterialStatus.pending_vectorization
            ).values(status=MaterialStatus.vectorized)
        )

    # delete all material marked for deletion 
    db_session.exec(
        delete(Material).where(Material.status == MaterialStatus.removed)
    )
    db_session.commit()
