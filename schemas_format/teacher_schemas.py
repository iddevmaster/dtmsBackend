from datetime import date, datetime
from typing import Optional, List

from pydantic import BaseModel

from schemas_format.school_schemas import (BranchRequestOutSchema,
                                           SchoolRequestOutSchema)

# User


class TeacherRequestInSchema(BaseModel):
    teacher_prefix: Optional[str] = None
    teacher_firstname: Optional[str] = None
    teacher_lastname: Optional[str] = None
    teacher_id_number: Optional[str] = None
    teacher_gender: Optional[int] = None
    teacher_phone: Optional[str] = None
    teacher_email: Optional[str] = None
    teacher_cover: Optional[str] = None
    active: Optional[int] = None
    branch_id: Optional[str] = None
    school_id: Optional[str] = None

    class Config:
        orm_mode = True


class TeacherRequestOutSchema(BaseModel):
    teacher_id: Optional[str] = None
    teacher_prefix: Optional[str] = None
    teacher_firstname: Optional[str] = None
    teacher_lastname: Optional[str] = None
    teacher_id_number: Optional[str] = None
    teacher_gender: Optional[int] = None
    teacher_phone: Optional[str] = None
    teacher_email: Optional[str] = None
    teacher_cover: Optional[str] = None
    active: Optional[int] = None
    cancelled: Optional[int] = None
    create_date: Optional[datetime] = None
    update_date: Optional[datetime] = None
    branch_id: Optional[str] = None
    school_id: Optional[str] = None
    branch_teacher: BranchRequestOutSchema
    school_teacher: SchoolRequestOutSchema

    class Config:
        orm_mode = True


class TeacherRequestOutOptionSchema(BaseModel):
    status: str
    status_code: str
    message: str
    page: int
    per_page: int
    total_page: int
    total_data: int
    total_filter_data: int
    data: List[TeacherRequestOutSchema]


class TeacherLicenceRequestInSchema(BaseModel):
    tl_number: Optional[str] = None
    tl_level: Optional[int] = None
    tl_date_of_expiry_staff: Optional[date] = None
    tl_date_of_issue: Optional[date] = None
    tl_date_of_expiry: Optional[date] = None
    vehicle_type_id: Optional[int] = None
    teacher_id: Optional[str] = None

    class Config:
        orm_mode = True


class TeacherLicenceRequestOutSchema(BaseModel):
    tl_id: Optional[int] = None
    tl_number: Optional[str] = None
    tl_level: Optional[int] = None
    tl_date_of_expiry_staff: Optional[date] = None
    tl_date_of_issue: Optional[date] = None
    tl_date_of_expiry: Optional[date] = None
    vehicle_type_id: Optional[int] = None
    teacher_id: Optional[str] = None
    teacher_teacherlicence: TeacherRequestOutSchema

    class Config:
        orm_mode = True


class TeacherIncomeRequestInSchema(BaseModel):
    ti_amount: Optional[float] = None
    ti_amount_type: Optional[int] = None
    ti_unit: Optional[int] = None
    ti_unit_type: Optional[int] = None
    subject_learn_type: Optional[int] = None
    vehicle_type_id: Optional[int] = None
    teacher_id: Optional[str] = None

    class Config:
        orm_mode = True


class TeacherIncomeRequestOutSchema(BaseModel):
    ti_id: Optional[int] = None
    ti_amount: Optional[float] = None
    ti_amount_type: Optional[int] = None
    ti_unit: Optional[int] = None
    ti_unit_type: Optional[int] = None
    subject_learn_type: Optional[int] = None
    vehicle_type_id: Optional[int] = None
    teacher_id: Optional[str] = None
    teacher_teacherincome: TeacherRequestOutSchema

    class Config:
        orm_mode = True
