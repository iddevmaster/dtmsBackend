from datetime import date, datetime, time
from typing import Optional, List

from pydantic import BaseModel
from schemas_format.school_schemas import BranchRequestOutSchema, SchoolRequestOutSchema
from schemas_format.teacher_schemas import TeacherRequestOutSchema


class SubjectRequestInSchema(BaseModel):
    subject_code: Optional[str] = None
    subject_name: Optional[str] = None
    subject_type: Optional[int] = None
    subject_learn_type: Optional[int] = None
    active: Optional[int] = None
    vehicle_type_id: Optional[int] = None
    school_id: Optional[str] = None

    class Config:
        orm_mode = True


class SubjectRequestOutSchema(BaseModel):
    subject_id: Optional[int] = None
    subject_code: Optional[str] = None
    subject_name: Optional[str] = None
    subject_type: Optional[int] = None
    subject_learn_type: Optional[int] = None
    active: Optional[int] = None
    create_date: Optional[datetime] = None
    update_date: Optional[datetime] = None
    vehicle_type_id: Optional[int] = None
    school_id: Optional[str] = None
    school_subject: SchoolRequestOutSchema

    class Config:
        orm_mode = True


class SubjectRequestOutOptionSchema(BaseModel):
    status: str
    status_code: str
    message: str
    page: int
    per_page: int
    total_page: int
    total_data: int
    total_filter_data: int
    data: List[SubjectRequestOutSchema]


class CourseRequestInSchema(BaseModel):
    course_code: Optional[str] = None
    course_name: Optional[str] = None
    course_theory_hour: Optional[float] = None
    course_practice_hour: Optional[float] = None
    course_total_hour: Optional[float] = None
    course_readey: Optional[int] = None
    course_group: Optional[int] = None
    active: Optional[int] = None
    vehicle_type_id: Optional[int] = None
    school_id: Optional[str] = None

    class Config:
        orm_mode = True


class CourseRequestOutSchema(BaseModel):
    course_id: Optional[str] = None
    course_code: Optional[str] = None
    course_name: Optional[str] = None
    course_theory_hour: Optional[float] = None
    course_practice_hour: Optional[float] = None
    course_total_hour: Optional[float] = None
    course_readey: Optional[int] = None
    course_group: Optional[int] = None
    active: Optional[int] = None
    cancelled: Optional[int] = None
    create_date: Optional[datetime] = None
    update_date: Optional[datetime] = None
    vehicle_type_id: Optional[int] = None
    school_id: Optional[str] = None
    school_course: SchoolRequestOutSchema

    class Config:
        orm_mode = True


class CourseRequestOutOptionSchema(BaseModel):
    status: str
    status_code: str
    message: str
    page: int
    per_page: int
    total_page: int
    total_data: int
    total_filter_data: int
    data: List[CourseRequestOutSchema]


class CoursePriceRequestInSchema(BaseModel):
    cp_price: Optional[float] = None
    course_id: Optional[str] = None
    branch_id: Optional[str] = None
    school_id: Optional[str] = None

    class Config:
        orm_mode = True


class SubjectCourseRequestInSchema(BaseModel):
    learn_time: Optional[float] = None
    subject_learn_type: Optional[int] = None
    subject_id: Optional[int] = None
    course_id: Optional[str] = None

    class Config:
        orm_mode = True


class SubjectCourseRequestOutSchema(BaseModel):
    cws_id: Optional[str] = None
    learn_time: Optional[float] = None
    subject_learn_type: Optional[int] = None
    subject_id: Optional[int] = None
    course_id: Optional[str] = None
    course_coursewithsubject: CourseRequestOutSchema
    subject_coursewithsubject: SubjectRequestOutSchema

    class Config:
        orm_mode = True


class SeminarRequestInSchema(BaseModel):
    seminar_start_time: Optional[time] = None
    seminar_end_time: Optional[time] = None
    seminar_date: Optional[date] = None
    seminar_ready: Optional[int] = None
    active: Optional[int] = None
    course_id: Optional[str] = None
    subject_id: Optional[int] = None
    teacher_id: Optional[str] = None
    branch_id: Optional[str] = None
    school_id: Optional[str] = None

    class Config:
        orm_mode = True


class SeminarRequestMutipleInSchema(BaseModel):
    seminar_start_time: Optional[time] = None
    seminar_end_time: Optional[time] = None
    subject_id: Optional[int] = None
    course_id: Optional[str] = None
    teacher_id: Optional[str] = None
    branch_id: Optional[str] = None
    school_id: Optional[str] = None
    seminar_date_Obj: Optional[list] = None

    class Config:
        orm_mode = True


class SeminarRequestOutSchema(BaseModel):
    seminar_id: Optional[int] = None
    seminar_start_time: Optional[time] = None
    seminar_end_time: Optional[time] = None
    seminar_hour: Optional[float] = None
    seminar_date: Optional[date] = None
    seminar_ready: Optional[int] = None
    active: Optional[int] = None
    create_date: Optional[datetime] = None
    update_date: Optional[datetime] = None
    course_id: Optional[str] = None
    subject_id: Optional[int] = None
    teacher_id: Optional[str] = None
    branch_id: Optional[str] = None
    school_id: Optional[str] = None
    subject_seminar: SubjectRequestOutSchema
    course_seminar: CourseRequestOutSchema
    teacher_seminar: TeacherRequestOutSchema
    branch_seminar: BranchRequestOutSchema
    school_seminar: SchoolRequestOutSchema

    class Config:
        orm_mode = True


class ExamDateRequestInSchema(BaseModel):
    ed_start_time: Optional[time] = None
    ed_end_time: Optional[time] = None
    ed_date: Optional[date] = None
    ed_ready: Optional[int] = None
    ed_code: Optional[str] = None
    active: Optional[int] = None
    vehicle_type_id: Optional[int] = None
    branch_id: Optional[str] = None
    school_id: Optional[str] = None

    class Config:
        orm_mode = True


class ExamDateRequestOutSchema(BaseModel):
    ed_id: Optional[int] = None
    ed_start_time: Optional[time] = None
    ed_end_time: Optional[time] = None
    ed_hour: Optional[float] = None
    ed_date: Optional[date] = None
    ed_ready: Optional[int] = None
    ed_code: Optional[str] = None
    active: Optional[int] = None
    create_date: Optional[datetime] = None
    update_date: Optional[datetime] = None
    vehicle_type_id: Optional[int] = None
    branch_id: Optional[str] = None
    school_id: Optional[str] = None
    branch_examdate: BranchRequestOutSchema
    school_examdate: SchoolRequestOutSchema

    class Config:
        orm_mode = True


class ExamDateDirectorRequestInSchema(BaseModel):
    ed_code: Optional[str] = None
    staff_exam_type: Optional[int] = None
    teacher_id: Optional[str] = None

    class Config:
        orm_mode = True


class ExamDateDirectorRequestOutSchema(BaseModel):
    edd_id: Optional[int] = None
    ed_code: Optional[str] = None
    staff_exam_type: Optional[int] = None
    teacher_id: Optional[str] = None
    teacher_examdate_dt: TeacherRequestOutSchema

    class Config:
        orm_mode = True
