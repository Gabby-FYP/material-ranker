from typing import Literal
from fastapi import UploadFile
from pydantic import UUID4, BaseModel, AnyUrl
from datetime import datetime


class MaterailRecommendation(BaseModel):
    material_id: UUID4
    material_title: str
    status: Literal['pending', 'approved', 'rejected']
    external_download_link: AnyUrl | None
    recommender_matric_no: str
    recommendation_datetime: datetime
    

class AdminDashboardDetails(BaseModel):
    user_count: int
    material_count: int
    pending_review_count: int
    pending_unvectorization_count: int
