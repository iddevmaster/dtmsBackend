from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

# User


class SchoolRequestInSchema(BaseModel):
    school_name: Optional[str] = None
    active: Optional[int] = None

    class Config:
        orm_mode = True


class SchoolRequestOutSchema(BaseModel):
    school_id: Optional[str] = None
    school_name: Optional[str] = None
    school_description: Optional[str] = None
    school_address: Optional[str] = None
    location_id: Optional[int] = None
    active: Optional[int] = None
    create_date: Optional[datetime] = None
    update_date: Optional[datetime] = None
    location_school:  Optional[object] = None

    class Config:
        orm_mode = True


class SchoolRequestOutOptionSchema(BaseModel):
    status: str
    status_code: str
    message: str
    page: int
    per_page: int
    total_page: int
    total_data: int
    total_filter_data: int
    data: List[SchoolRequestOutSchema]


class BranchRequestInSchema(BaseModel):
    branch_code: Optional[str] = None
    branch_name: Optional[str] = None
    active: Optional[int] = None
    school_id: Optional[str] = None

    class Config:
        orm_mode = True


class BranchRequestOutSchema(BaseModel):
    branch_id: Optional[str] = None
    branch_code: Optional[str] = None
    branch_name: Optional[str] = None
    active: Optional[int] = None
    create_date: Optional[datetime] = None
    update_date: Optional[datetime] = None
    school_id: Optional[str] = None

    class Config:
        orm_mode = True


class BranchRequestOutOptionSchema(BaseModel):
    status: str
    status_code: str
    message: str
    page: int
    per_page: int
    total_page: int
    total_data: int
    total_filter_data: int
    data: List[BranchRequestOutSchema]
