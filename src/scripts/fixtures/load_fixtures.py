from sqlmodel import Session
from src.models import AdminUser
from sqlmodel import select
from sqlalchemy.exc import SQLAlchemyError
from src.core.config import settings
from src.core.security import get_password_hash
from src.libs.log import logger


def load_fixtures(session: Session) -> None:
    """Load fixtures into the database."""
    logger.info("Loading fixtures")    
    __create_first_admin_user(session)

    logger.info("Fixtures loaded")    


def __create_first_admin_user(session: Session) -> None:
    """Load admin user fixtures."""

    try: 
        # first check if the admin user already exists
        admin_user = session.exec(
            select(AdminUser).where(
                AdminUser.is_superuser == True,
                AdminUser.email == settings.FIRST_SUPERUSER_EMAIL,
            )
        ).first()

        if not admin_user:
            # create the first admin user
            frist_admin_user = AdminUser(
                email=settings.FIRST_SUPERUSER_EMAIL,
                fullname=settings.FIRST_SUPERUSER,
                password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
                is_superuser=True,
                is_active=True,
            )

            session.add(frist_admin_user)
            session.commit()
    except SQLAlchemyError as error:
        logger.error(f"Error creating first admin user: {error}")
        session.rollback()
        