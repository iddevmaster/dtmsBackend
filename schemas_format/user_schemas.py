from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from schemas_format.school_schemas import (BranchRequestOutSchema,
                                           SchoolRequestOutSchema)
# User


class UserRequestInSchema(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    user_type: Optional[int] = None
    active: Optional[int] = None
    branch_id: Optional[str] = None
    school_id: Optional[str] = None

    class Config:
        orm_mode = True


class UserRequestOutSchema(BaseModel):
    user_id: Optional[str] = None
    username: Optional[str] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    user_type: Optional[int] = None
    active: Optional[int] = None
    cancelled: Optional[int] = None
    create_date: Optional[datetime] = None
    branch_id: Optional[str] = None
    school_id: Optional[str] = None
    branch_user: Optional[BranchRequestOutSchema] = None
    school_user:  Optional[SchoolRequestOutSchema] = None

    class Config:
        orm_mode = True


class UserRequestOutOptionSchema(BaseModel):
    status: str
    status_code: str
    message: str
    page: int
    per_page: int
    total_page: int
    total_data: int
    total_filter_data: int
    data: List[UserRequestOutSchema]


class UserLoginSchema(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    school_id: Optional[str] = None

    class Config:
        orm_mode = True
