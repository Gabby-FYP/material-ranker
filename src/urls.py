from fastapi import APIRouter
from src.site.router import router as site_router

routes = APIRouter()
routes.include_router(site_router)
