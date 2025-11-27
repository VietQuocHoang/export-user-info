from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from db.engine import get_engine
from models import Organization, User
from schemas.users import FilterParam
from services import user_services

router = APIRouter()


@router.get("/users", tags=["users"])
async def get_users(
    query_params: Annotated[FilterParam, Query()], engine: Engine = Depends(get_engine)
):
    return user_services.get_user_list(query_params, engine)


@router.get("/users/filters", tags=["users"])
async def get_filter_values(engine: Engine = Depends(get_engine)):
    return user_services.get_filter_values(engine=engine)
