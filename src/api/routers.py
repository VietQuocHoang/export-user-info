from fastapi import APIRouter

from .v1 import *

router = APIRouter(prefix="/api/v1")
router.include_router(router=user_router)
