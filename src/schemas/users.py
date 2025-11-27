import enum
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from models.users import StatusEnum


class FilterParam(BaseModel):
    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)
    status: List[
        Literal[StatusEnum.ACTIVE.value, StatusEnum.TERMINATED.value, StatusEnum.NOT_STARTED.value]
    ] = []
    location: Optional[str] = ""
    department: Optional[str] = ""
    position: Optional[str] = ""
    org_id: Optional[int] = None
