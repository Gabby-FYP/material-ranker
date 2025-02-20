from fastapi import APIRouter
from src.site.routes.auth import router as auth_router
from src.site.routes.materials import router as materials_router
from src.site.routes.admin import router as admin_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(materials_router, prefix="/materials")
router.include_router(admin_router, prefix="/admin_dashboard")