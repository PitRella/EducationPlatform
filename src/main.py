from fastapi import FastAPI, APIRouter

from src.users.router import user_router
from src.auth.router import auth_router

app = FastAPI(title="EducationPlatform")

main_api_router = APIRouter(prefix="/api/v1")
main_api_router.include_router(user_router, prefix="/user", tags=["user"])
main_api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(main_api_router)
