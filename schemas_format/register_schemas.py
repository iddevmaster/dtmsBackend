from datetime import date, datetime, time
from typing import List, Optional

from pydantic import BaseModel
from schemas_format.school_schemas import BranchRequestOutSchema, SchoolRequestOutSchema


class SearchScheduleInSchema(BaseModel):
    course_id: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    date_set: Optional[date] = None
    teacher_id: Optional[str] = None
    branch_id: Optional[str] = None
    school_id: Optional[str] = None

    class Config:
        orm_mode = True


class RegisterMainUpdateInSchema(BaseModel):
    rm_pay_status: Optional[str] = None
    rm_status: Optional[str] = None
    ed_id: Optional[str] = None

    class Config:
        orm_mode = True


class RegisterMainOutSchema(BaseModel):
    rm_id: Optional[str] = None
    rm_doc_number: Optional[str] = None
    rm_pay_status: Optional[str] = None
    rm_status: Optional[str] = None
    course_group: Optional[str] = None
    vehicle_type_id: Optional[str] = None
    create_date: Optional[datetime] = None
    update_date: Optional[datetime] = None
    course_id: Optional[str] = None
    ed_id: Optional[int] = None
    branch_id: Optional[str] = None
    school_id: Optional[str] = None

    class Config:
        orm_mode = True


class RegisterScheduleInSchema(BaseModel):
    subject_learn_type: Optional[int] = None
    rs_start_time: Optional[datetime] = None
    rs_end_time: Optional[datetime] = None
    # rs_hour: Optional[float] = None
    subject_id: Optional[int] = None
    teacher_id: Optional[str] = None
    rm_id: Optional[str] = None
    branch_id: Optional[str] = None
    school_id: Optional[str] = None

    class Config:
        orm_mode = True


class RegisterScheduleInUpdateSchema(BaseModel):
    rs_start_time: Optional[datetime] = None
    rs_end_time: Optional[datetime] = None

    class Config:
        orm_mode = True


class RegisterScheduleOutSchema(BaseModel):
    rs_id: Optional[str] = None
    subject_learn_type: Optional[int] = None
    rs_start_time: Optional[datetime] = None
    rs_end_time: Optional[datetime] = None
    rs_hour: Optional[float] = None
    rs_check: Optional[int] = None
    create_date: Optional[datetime] = None
    update_date: Optional[datetime] = None
    subject_id: Optional[int] = None
    teacher_id: Optional[str] = None
    rm_id: Optional[str] = None
    branch_id: Optional[str] = None
    school_id: Optional[str] = None
    join_subject_learn_type: Optional[str] = None
    join_subject_id: Optional[str] = None
    join_teacher_id: Optional[str] = None

    class Config:
        orm_mode = True


class RegisterStudentInSchema(BaseModel):
    student_cover: Optional[str] = None
    student_prefix: Optional[str] = None
    student_firstname: Optional[str] = None
    student_lastname: Optional[str] = None
    student_id_number: Optional[str] = None
    student_birthday: Optional[date] = None
    student_gender: Optional[int] = None
    student_mobile: Optional[str] = None
    student_email: Optional[str] = None
    student_address: Optional[str] = None
    location_id: Optional[int] = None
    country_id: Optional[int] = None
    nationality_id: Optional[int] = None
    rm_id: Optional[str] = None
    branch_id: Optional[str] = None
    school_id: Optional[str] = None

    class Config:
        orm_mode = True


class PaymentRegisterListInSchema(BaseModel):
    pl_name: Optional[str] = None
    pl_unit: Optional[float] = None
    pl_price_per_unit: Optional[float] = None
    pl_price_sum: Optional[float] = None

    class Config:
        orm_mode = True


class PaymentRegisterInSchema(BaseModel):
    pr_name: Optional[str] = None
    pr_tax_number: Optional[str] = None
    pr_address: Optional[str] = None
    pr_discount_percent: Optional[float] = None
    pr_discount_amount: Optional[float] = None
    pr_total_amount: Optional[float] = None
    pr_pay: Optional[float] = None
    pr_debt: Optional[float] = None
    pr_remark: Optional[str] = None
    pr_receipt_issuer: Optional[str] = None
    rm_id: Optional[str] = None
    line: List[PaymentRegisterListInSchema]

    class Config:
        orm_mode = True
