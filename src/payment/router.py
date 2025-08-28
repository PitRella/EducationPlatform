from fastapi import APIRouter

from src.courses.schemas import (
    BaseCourseResponseSchema,

)

payment_router = APIRouter()


@payment_router.post('/')
async def create_payment(
) -> BaseCourseResponseSchema:
    pass
