from fastapi import APIRouter
from src.site.routes.users import router as user_router
from src.site.routes.materials import router as materials_router
from src.site.routes.admin import router as admin_router
from src.site.routes.site import router as sites_router


router = APIRouter()


router.include_router(sites_router, tags=['site'])
router.include_router(user_router, prefix='/accounts', tags=['user'])
router.include_router(materials_router, prefix="/materials", tags=['material'])
router.include_router(admin_router, prefix="/admin", tags=['admin'])
