from fastapi import Depends, Query, UploadFile, status, File, Form, Path
from typing import Annotated
from pydantic import AnyUrl, UUID4
from sqlmodel import Session, select, col, func
from src.core.dependecies import (
    require_admin_or_user_access,
    require_db_session, 
    require_authenticated_admin_user_session,
    require_authenticated_user_session,
)
from src.libs.exceptions import ServiceError
from src.libs.utils import CeleryHelper
from src.material.schemas import AdminDashboardDetails, MaterailRecommendation
from src.material.tfid.vectorizer import Vectorizer, VectorizerNotFound
from src.models import AdminUser, Material, MaterialRating, MaterialStatus, MaterialVector, User, UserMaterial
from src.material.tasks import synchronize_documents_tasks
from sqlalchemy.exc import SQLAlchemyError
from src.libs.log import logger
from sqlalchemy_file.exceptions import ContentTypeValidationError, SizeValidationError
from src.core.config import settings


def create_material_service(
    session: Annotated[Session, Depends(require_db_session)],
    admin_or_user: Annotated[
        AdminUser | User,
        Depends(require_admin_or_user_access)
    ],
    title: Annotated[str, Form()],
    description: Annotated[str, Form()],
    author: Annotated[str, Form()],
    content: Annotated[UploadFile, File()],
    cover_image: Annotated[UploadFile | None, File()] = None,
    external_download_url: Annotated[AnyUrl | None, Form()] = None,
) -> Material:
    """Create a new material."""

    try:
        vector = MaterialVector()
        material = Material(
            title=title, 
            description=description,
            authors=author,
            content=content,
            cover_image=cover_image,
            external_download_url=str(external_download_url) if external_download_url else None,
            status=(
                MaterialStatus.pending_vectorization 
                if isinstance(admin_or_user, AdminUser) else
                MaterialStatus.pending_approval 
            ),
            vector=vector,
        )

        to_create = [vector, material]

        # if material is created by user, create recommendation model
        if isinstance(admin_or_user, User):
            recommendation = UserMaterial(
                user=admin_or_user,
                material=material,
            )
            to_create.append(recommendation)

        session.add_all(to_create)
        session.commit()
        session.refresh(material)
    except SQLAlchemyError as error:
        session.rollback()
        logger.error(f"Error resetting password: {error}")
        raise ServiceError(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while submitting material.",
        ) from error
    except SizeValidationError as error:
        session.rollback()
        raise ServiceError(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File size too large.",
        ) from error
    except ContentTypeValidationError as error:
        session.rollback()
        raise ServiceError(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Invalid file type.",
        ) from error

    return material


def synchronize_service(
    session: Annotated[Session, Depends(require_db_session)],
    admin: Annotated[AdminUser, Depends(require_authenticated_admin_user_session)],
) -> None:
    """Revectorize all materials."""

    # ensure that we cant trigger synchronization while service is already running
    if not CeleryHelper.is_being_executed('synchronize_documents_tasks'):
        synchronize_documents_tasks.apply_async()
    else:
        raise ServiceError(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error: Vectocrs are already being sychronized please be patient.",
        )


def _get_combined_score(
    cosine_similarities: list[float],
    normalized_user_ratings: list[float],
) -> list[float]:
    weight = settings.COSINE_SIMILARITY_WEIGHT

    return [
        weight * cos_sim + (1 - weight) * norm_rating 
        for cos_sim, norm_rating in zip(cosine_similarities, normalized_user_ratings)
    ]


def material_search_service(
    session: Annotated[Session, Depends(require_db_session)],
    admin_or_user: Annotated[
        AdminUser | User,
        Depends(require_admin_or_user_access)
    ],
    search_query: Annotated[str, Query()],
    limit: Annotated[int, Query()] = 10,
) -> list[Material]:
    """Perform TFIDF search and reorder results based on combined score."""
    
    try:
        search_indexes, cosine_similarity = Vectorizer().search(query=search_query, limit=limit)
    except VectorizerNotFound as error:
        raise ServiceError(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occured during search. Please reach out to admin to re-vectorize",
        ) from error

    if not search_indexes:
        return []

    # Select vectorized materials
    materials = session.exec(
        select(Material).where(
            Material.status == MaterialStatus.vectorized
        ).order_by(col(Material.vector_id))
    ).all()
    
    initial_search_results = [materials[index] for index in search_indexes]
    normalized_user_ratings = [
        material.normalized_average_rating 
        for material in initial_search_results
    ]

    combined_score = _get_combined_score(
        cosine_similarities=cosine_similarity,
        normalized_user_ratings=normalized_user_ratings
    )
    
    # Re-arrange initial search result using combined score
    sorted_results = sorted(
        zip(initial_search_results, combined_score),
        key=lambda x: x[1],  # Sort by combined_score (second element of each pair)
        reverse=True         # Descending order (highest score first)
    )

    search_results = [material for material, _ in sorted_results]
    return search_results


def admin_material_list_service(
    session: Annotated[Session, Depends(require_db_session)],
    admin: Annotated[AdminUser, Depends(require_authenticated_admin_user_session)],
) -> list[Material]:
    """List all materials on the platform."""
    
    return session.exec(
        select(Material).where(
            col(Material.status).in_(
                [
                    MaterialStatus.vectorized, 
                    MaterialStatus.removed,
                    MaterialStatus.pending_vectorization,
                ]
            )
        ).order_by(col(Material.vector_id))
    ).all()


def get_material_service(
    session: Annotated[Session, Depends(require_db_session)],
    material_id: Annotated[UUID4, Path()],
) -> Material:
    """Get a material."""

    material = session.exec(
        select(Material).where(
            Material.id == material_id,
            Material.status == MaterialStatus.vectorized,
        )
    ).first()
    
    if not material:
        raise ServiceError(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Material not found.",
        )
    
    return material


def check_user_has_rated_material(session: Session, user: User, material: Material) -> bool:
    """Check if user has already rated a material."""
    return bool(
        session.exec(
            select(MaterialRating).where(
                MaterialRating.user_id == user.id,
                MaterialRating.material_id == material.id,
            )
        ).first()
    )


def material_user_rating_count(
    session: Session, material: Material
) -> int:
    """Return the total number of users who have rated materials."""
    return session.exec(
        select(func.count(col(MaterialRating.material_id))).where(
            MaterialRating.material_id == material.id
        )
    ).first() or 0


def material_recommendation_list_service(
    session: Annotated[Session, Depends(require_db_session)],
    admin: Annotated[AdminUser, Depends(require_authenticated_admin_user_session)],
) -> list[MaterailRecommendation]:
    """list recommended materials."""
    user_recommendations = session.exec(
        select(UserMaterial).join(
            Material,
            UserMaterial.material_id == Material.id,
        ).where(
            Material.status == MaterialStatus.pending_approval,
        )
    )

    return [
        MaterailRecommendation(
            status='pending',
            material_id=recommendation.material_id,
            material_title=recommendation.material.title,
            recommender_matric_no=str(recommendation.user.matric_number),
            recommendation_datetime=recommendation.material.created_datetime,
            external_download_link=recommendation.material.external_download_url,
        )
        for recommendation in user_recommendations
    ]


def user_material_recommendation_list(
    session: Annotated[Session, Depends(require_db_session)],
    user: Annotated[User, Depends(require_authenticated_user_session)],
) -> list[MaterailRecommendation]:
    """List materials recommended by a specific user."""

    user_recommendations = session.exec(
        select(UserMaterial).join(
            Material,
            UserMaterial.material_id == Material.id,
        ).where(
            UserMaterial.user_id == user.id,
            col(Material.status).not_in([MaterialStatus.removed])
        )
    )

    recommendation_status = {
        MaterialStatus.pending_approval: 'pending',
        MaterialStatus.pending_vectorization: 'approved',
        MaterialStatus.vectorized: 'approved',
        MaterialStatus.rejected: 'rejected',
    }

    return [
        MaterailRecommendation(
            status=recommendation_status[recommendation.material.status],
            material_id=recommendation.material_id,
            material_title=recommendation.material.title,
            recommender_matric_no=str(recommendation.user.matric_number),
            recommendation_datetime=recommendation.material.created_datetime,
            external_download_link=recommendation.material.external_download_url,
        )
        for recommendation in user_recommendations
    ]


def approve_material_recommendation_serivce(
    session: Annotated[Session, Depends(require_db_session)],
    admin: Annotated[AdminUser, Depends(require_authenticated_admin_user_session)],
    material_id: Annotated[UUID4, Path()],
) -> Material:
    """Approve a recommended material."""
    
    material = session.exec(
        select(Material).where(
            Material.id == material_id,
            Material.status == MaterialStatus.pending_approval,
        )
    ).first()
    
    if not material:
        raise ServiceError(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Material not found.",
        )

    material.status = MaterialStatus.pending_vectorization
    session.add(material)
    session.commit()
    
    return material


def reject_material_recommendation_serivce(
    session: Annotated[Session, Depends(require_db_session)],
    admin: Annotated[AdminUser, Depends(require_authenticated_admin_user_session)],
    material_id: Annotated[UUID4, Path()],
) -> Material:
    """Approve a recommended material."""
    
    material = session.exec(
        select(Material).where(
            Material.id == material_id,
            Material.status == MaterialStatus.pending_approval,
        )
    ).first()
    
    if not material:
        raise ServiceError(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Material not found.",
        )

    material.status = MaterialStatus.rejected
    session.add(material)
    session.commit()

    return material


def _update_material_rating(
    session: Annotated[Session, Depends(require_db_session)],
    material: Annotated[Material, Depends(get_material_service)],    
) -> Material:
    """Recalculate a materials rating."""
    
    ratings = session.exec(select(MaterialRating).where(
        MaterialRating.material_id == material.id
    )).all()

    if ratings:
        average_rating = sum([rating.rating for rating in ratings]) / len(ratings)
        material.average_rating = average_rating
        session.add(material)
        session.commit()
        session.refresh(material)

    return material


def rate_material_service(
    session: Annotated[Session, Depends(require_db_session)],
    user: Annotated[User, Depends(require_authenticated_user_session)],
    material: Annotated[Material, Depends(get_material_service)],
    rating: Annotated[int, Form(ge=1, le=5)],   
) -> Material:
    """Rate a material average rating."""

    # check if the user recommmended this material
    if session.exec(select(UserMaterial).where(
        UserMaterial.user_id == user.id,
        UserMaterial.material_id == material.id,
    )).first():
        raise ServiceError(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error: You are not allowed to rate a material you recommended.",
        )

    # check if the user has rated this material before
    material_rating = session.exec(select(MaterialRating).where(
        MaterialRating.user_id == user.id,
        MaterialRating.material_id == material.id
    )).first()
    
    if not material_rating:
        material_rating = MaterialRating(user=user, material=material, rating=rating)

    material_rating.rating = rating
    session.add(material_rating)
    session.commit()

    material = _update_material_rating(
        session=session,
        material=material,
    )

    return material


def mark_material_for_removal_service(
    session: Annotated[Session, Depends(require_db_session)],
    admin: Annotated[AdminUser, Depends(require_authenticated_admin_user_session)],
    material_id: Annotated[UUID4, Path()],
) -> None:
    """Get a material."""

    material = session.exec(
        select(Material).where(
            Material.id == material_id,
            col(Material.status).in_(
                [
                    MaterialStatus.vectorized,
                    MaterialStatus.pending_vectorization,
                ]
            ),
        )
    ).first()
    
    if not material:
        raise ServiceError(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Material not found.",
        )

    if material.status == MaterialStatus.pending_vectorization:
        # material has not been vectorized we can delete it directly
        session.delete(material)
        session.commit()
    else:
        material.status = MaterialStatus.removed
        session.add(material)
        session.commit()


def get_admin_dashboard_detail_service(
    session: Annotated[Session, Depends(require_db_session)],
    admin: Annotated[AdminUser, Depends(require_authenticated_admin_user_session)],
) -> AdminDashboardDetails:
    """Retrieve admin dashboard details."""
    
    # count number of users on platform
    user_count = session.exec(select(func.count(col(User.id)))).first()
    material_count = session.exec(
        select(func.count(col(Material.id))).where(
            Material.status == MaterialStatus.vectorized
        )
    ).first()
    pending_review_count = session.exec(
        select(func.count(col(Material.id))).where(
            Material.status == MaterialStatus.pending_approval
        )        
    ).first()
    pending_unvectorization_count = session.exec(
        select(func.count(col(Material.id))).where(
            col(Material.status).in_([
                MaterialStatus.removed,
                MaterialStatus.pending_vectorization,
            ])
        )        
    ).first()

    return AdminDashboardDetails(
        user_count=user_count,
        material_count=material_count,
        pending_review_count=pending_review_count,
        pending_unvectorization_count=pending_unvectorization_count,
    )


def material_pending_vectorization_list_service(
    session: Annotated[Session, Depends(require_db_session)],
    admin: Annotated[AdminUser, Depends(require_authenticated_admin_user_session)],
) -> list[Material]:
    """List all materials on the platform."""
    
    return session.exec(
        select(Material).where(
            col(Material.status).in_(
                [
                    MaterialStatus.removed,
                    MaterialStatus.pending_vectorization,
                ]
            )
        ).order_by(col(Material.vector_id))
    ).all()


def user_material_list_service(
    session: Annotated[Session, Depends(require_db_session)],
    user: Annotated[User, Depends(require_authenticated_user_session)],
) -> list[Material]:
    """List all materials on the platform."""
    
    return session.exec(
        select(Material).where(
            Material.status == MaterialStatus.vectorized
        )
    ).all()

