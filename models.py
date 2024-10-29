from sqlalchemy import (Boolean, Column, Date, DateTime, Float, ForeignKey,
                        Integer, String, Time)
from sqlalchemy.orm import relationship
from typing import Any
from database import Base
from function import generateId, generateShortId

from sqlalchemy.ext.declarative import declarative_base

Base: Any = declarative_base()


class Country(Base):
    __tablename__ = 'app_country'
    country_id = Column(Integer, primary_key=True)
    country_name_th = Column(String(128), nullable=True)
    country_name_eng = Column(String(128), nullable=True)
    country_official_name_th = Column(String(128), nullable=True)
    country_official_name_eng = Column(String(128), nullable=True)
    capital_name_th = Column(String(128), nullable=True)
    capital_name_eng = Column(String(128), nullable=True)
    zone = Column(String(128), nullable=True)


class LocationThai(Base):
    __tablename__ = 'app_location_thai'
    location_id = Column(Integer, primary_key=True)
    district_code = Column(String(128), nullable=True)
    district_name = Column(String(128), nullable=True)
    zipcode = Column(String(128), nullable=True)
    amphur_code = Column(String(128), nullable=True)
    amphur_name = Column(String(128), nullable=True)
    province_code = Column(String(128), nullable=True)
    province_name = Column(String(128), nullable=True)
    location_student_tmp = relationship(
        "RegisterTmpStudent", back_populates="student_tmp_location")
    location_student_core = relationship(
        "RegisterCoreStudent", back_populates="student_core_location")
    school_location = relationship("School", back_populates="location_school")
# user_type : 1 =Super Admin , 2 = School Admin, 3 = User ,4 = teacher , 5 = student


class User(Base):
    __tablename__ = 'app_user'
    user_id = Column(String(128), primary_key=True,
                     unique=True, default=generateId)
    username = Column(String(128), index=True)
    password = Column(String(128), nullable=True)
    firstname = Column(String(128), nullable=True)
    lastname = Column(String(128), nullable=True)
    user_type = Column(Integer, default=0)
    active = Column(Integer, default=1)
    cancelled = Column(Integer, default=1)
    create_date = Column(DateTime)
    branch_id = Column(String(128), ForeignKey(
        "app_branch.branch_id", ondelete="CASCADE"))
    school_id = Column(String(128), ForeignKey(
        "app_school.school_id", ondelete="CASCADE"))

    branch_user = relationship("Branch", back_populates="user_branch")
    school_user = relationship("School", back_populates="user_school")


class School(Base):
    __tablename__ = 'app_school'
    school_id = Column(String(128), primary_key=True,
                       unique=True, default=generateId)
    school_name = Column(String(128), nullable=True)
    school_description = Column(String(256), nullable=True)
    school_address = Column(String(256), nullable=True)
    location_id = Column(Integer, ForeignKey(
        "app_location_thai.location_id", ondelete="CASCADE"), nullable=True)
    active = Column(Integer, default=1)
    cancelled = Column(Integer, default=1)
    create_date = Column(DateTime)
    update_date = Column(DateTime)
    location_school = relationship(
        "LocationThai", back_populates="school_location")
    user_school = relationship("User", back_populates="school_user")
    subject_school = relationship("Subject", back_populates="school_subject")
    course_school = relationship("Course", back_populates="school_course")
    teacher_school = relationship("Teacher", back_populates="school_teacher")
    seminar_school = relationship("Seminar", back_populates="school_seminar")
    examdate_school = relationship(
        "ExamDate", back_populates="school_examdate")
    regisetmain_tmp_school = relationship(
        "RegisterTmpMain", back_populates="school_regisetmain_tmp")
    regisetmain_core_school = relationship(
        "RegisterCoreMain", back_populates="school_regisetmain_core")


class Branch(Base):
    __tablename__ = 'app_branch'
    branch_id = Column(String(128), primary_key=True,
                       unique=True, default=generateShortId)
    branch_code = Column(String(128), nullable=False)
    branch_name = Column(String(128), nullable=False)
    active = Column(Integer, default=1)
    cancelled = Column(Integer, default=1)
    create_date = Column(DateTime)
    update_date = Column(DateTime)
    school_id = Column(String(128), ForeignKey(
        "app_school.school_id", ondelete="CASCADE"))

    user_branch = relationship("User", back_populates="branch_user")
    teacher_branch = relationship("Teacher", back_populates="branch_teacher")
    seminar_branch = relationship("Seminar", back_populates="branch_seminar")
    examdate_branch = relationship(
        "ExamDate", back_populates="branch_examdate")
    regisetmain_tmp_branch = relationship(
        "RegisterTmpMain", back_populates="branch_regisetmain_tmp")
    regisetmain_core_branch = relationship(
        "RegisterCoreMain", back_populates="branch_regisetmain_core")
    course_price_branch = relationship(
        "CoursePrice", back_populates="branch_course_price")
# subject_type 1 = วิชาบังคับ , 2 =วิชาเพิ่มเติม
# subject_learn_type 1 = ทฤษฏี , 2 =ปฏิบัติ


class Subject(Base):
    __tablename__ = 'app_subject'
    subject_id = Column(Integer, primary_key=True)
    subject_code = Column(String(128), nullable=False)
    subject_name = Column(String(128), nullable=False)
    subject_type = Column(Integer, nullable=False)
    subject_learn_type = Column(Integer, nullable=False)
    active = Column(Integer, default=1)
    cancelled = Column(Integer, default=1)
    create_date = Column(DateTime)
    update_date = Column(DateTime)
    vehicle_type_id = Column(Integer, nullable=False)
    school_id = Column(String(128), ForeignKey(
        "app_school.school_id", ondelete="CASCADE"))

    school_subject = relationship("School", back_populates="subject_school")
    coursewithsubject_subject = relationship(
        "CourseWithSubject", back_populates="subject_coursewithsubject")
    seminar_subject = relationship("Seminar", back_populates="subject_seminar")
    rts_subject = relationship(
        "RegisterTmpSchedule", back_populates="subject_rts")
    rcs_subject = relationship(
        "RegisterCoreSchedule", back_populates="subject_rcs")

# course_readey 0 = ยังไม่กำหนดรายวิชาหลักสูตร , 1 = กำหนดรายวิชาหลักสูตรแล้ว


class Course(Base):
    __tablename__ = 'app_course'
    course_id = Column(String(128), primary_key=True,
                       unique=True, default=generateShortId)
    course_code = Column(String(128), nullable=False)
    course_name = Column(String(128), nullable=False)
    course_theory_hour = Column(Float, nullable=False)
    course_practice_hour = Column(Float, nullable=False)
    course_total_hour = Column(Float, nullable=False)
    course_readey = Column(Integer, nullable=False)
    course_group = Column(Integer, nullable=False)
    active = Column(Integer, default=1)
    cancelled = Column(Integer, default=1)
    create_date = Column(DateTime)
    update_date = Column(DateTime)
    vehicle_type_id = Column(Integer, nullable=False)
    school_id = Column(String(128), ForeignKey(
        "app_school.school_id", ondelete="CASCADE"))

    school_course = relationship("School", back_populates="course_school")
    coursewithsubject_course = relationship(
        "CourseWithSubject", back_populates="course_coursewithsubject")
    seminar_course = relationship("Seminar", back_populates="course_seminar")
    regisetmain_tmp_course = relationship(
        "RegisterTmpMain", back_populates="course_regisetmain_tmp")
    regisetmain_core_course = relationship(
        "RegisterCoreMain", back_populates="course_regisetmain_core")


class CourseWithSubject(Base):
    __tablename__ = 'app_course_with_subject'
    cws_id = Column(String(128), primary_key=True,
                    unique=True, default=generateShortId)
    learn_time = Column(Float, nullable=False)
    subject_learn_type = Column(Integer, nullable=False)
    subject_id = Column(Integer, ForeignKey(
        "app_subject.subject_id"))
    course_id = Column(String(128), ForeignKey(
        "app_course.course_id"))

    subject_coursewithsubject = relationship(
        "Subject", back_populates="coursewithsubject_subject")
    course_coursewithsubject = relationship(
        "Course", back_populates="coursewithsubject_course")


class CoursePrice(Base):
    __tablename__ = 'app_course_price'
    cp_id = Column(Integer, primary_key=True)
    cp_price = Column(Float, nullable=False)
    course_id = Column(String(128), ForeignKey(
        "app_course.course_id", ondelete="CASCADE"))
    branch_id = Column(String(128), ForeignKey(
        "app_branch.branch_id", ondelete="CASCADE"))
    school_id = Column(String(128), ForeignKey(
        "app_school.school_id", ondelete="CASCADE"))
    branch_course_price = relationship(
        "Branch", back_populates="course_price_branch")


class Teacher(Base):
    __tablename__ = 'app_teacher'
    teacher_id = Column(String(128), primary_key=True,
                        unique=True, default=generateId)
    teacher_prefix = Column(String(128), nullable=True)
    teacher_firstname = Column(String(128), nullable=True)
    teacher_lastname = Column(String(128), nullable=True)
    teacher_id_number = Column(String(128), nullable=True)
    teacher_gender = Column(Integer, nullable=False)
    teacher_phone = Column(String(128), nullable=True)
    teacher_email = Column(String(128), nullable=True)
    teacher_cover = Column(String(128), nullable=True)
    active = Column(Integer, default=1)
    cancelled = Column(Integer, default=1)
    create_date = Column(DateTime)
    update_date = Column(DateTime)
    branch_id = Column(String(128), ForeignKey(
        "app_branch.branch_id", ondelete="CASCADE"))
    school_id = Column(String(128), ForeignKey(
        "app_school.school_id", ondelete="CASCADE"))

    branch_teacher = relationship("Branch", back_populates="teacher_branch")
    school_teacher = relationship("School", back_populates="teacher_school")
    seminar_teacher = relationship("Seminar", back_populates="teacher_seminar")
    teacherlicence_teacher = relationship(
        "TeacherLicense", back_populates="teacher_teacherlicence")
    teacherincome_teacher = relationship(
        "TeacherIncome", back_populates="teacher_teacherincome")
    examdate_dt_teacher = relationship(
        "ExamDateDirector", back_populates="teacher_examdate_dt")
    rts_teacher = relationship(
        "RegisterTmpSchedule", back_populates="teacher_rts")
    rcs_teacher = relationship(
        "RegisterCoreSchedule", back_populates="teacher_rcs")


class TeacherLicense(Base):
    __tablename__ = 'app_teacher_license'
    tl_id = Column(Integer, primary_key=True)
    tl_number = Column(String(128), nullable=True)
    tl_level = Column(Integer, nullable=True)
    tl_date_of_expiry_staff = Column(Date)
    tl_date_of_issue = Column(Date)
    tl_date_of_expiry = Column(Date)
    vehicle_type_id = Column(Integer, nullable=False)
    teacher_id = Column(String(128), ForeignKey(
        "app_teacher.teacher_id", ondelete="CASCADE"))

    teacher_teacherlicence = relationship(
        "Teacher", back_populates="teacherlicence_teacher")


#  tl_amount_type 1 =ค่าสอน ทฤษฎี และ ปฏิบัติ, 2 = กรรมการ , 3 = ประธาน ,4 = เงินเดือน ,
# ถ้าเป็น ทฤษฎี จะมีกรรมการ
# ถ้าเป็น ปฏิบัติ จะมีกรรมการและประธาน
# tl_unit_type 1 = รายชั่วโมง , 2 = รายวัน , 3 = รายเดือน , 4 = รายคน


class TeacherIncome(Base):
    __tablename__ = 'app_teacher_income'
    ti_id = Column(Integer, primary_key=True)
    ti_amount = Column(Float, nullable=True)
    ti_amount_type = Column(Integer, nullable=True)
    ti_unit = Column(Integer, nullable=True)
    ti_unit_type = Column(Integer, nullable=True)
    subject_learn_type = Column(Integer, nullable=False)
    vehicle_type_id = Column(Integer, nullable=False)
    teacher_id = Column(String(128), ForeignKey(
        "app_teacher.teacher_id", ondelete="CASCADE"))

    teacher_teacherincome = relationship(
        "Teacher", back_populates="teacherincome_teacher")

# seminar_confirm 0 = ยังสามารถแก้ไขได้ , 1 = ยืนยันการนำไปใช้


class Seminar(Base):
    __tablename__ = 'app_seminar'
    seminar_id = Column(Integer, primary_key=True)
    seminar_start_time = Column(Time)
    seminar_end_time = Column(Time)
    seminar_hour = Column(Float, nullable=False)
    seminar_date = Column(Date)
    seminar_ready = Column(Integer, default=0)
    active = Column(Integer, default=1)
    cancelled = Column(Integer, default=1)
    create_date = Column(DateTime)
    update_date = Column(DateTime)
    subject_id = Column(Integer, ForeignKey(
        "app_subject.subject_id", ondelete="CASCADE"))
    course_id = Column(String(128), ForeignKey(
        "app_course.course_id", ondelete="CASCADE"))
    teacher_id = Column(String(128), ForeignKey(
        "app_teacher.teacher_id", ondelete="CASCADE"))
    branch_id = Column(String(128), ForeignKey(
        "app_branch.branch_id", ondelete="CASCADE"))
    school_id = Column(String(128), ForeignKey(
        "app_school.school_id", ondelete="CASCADE"))

    subject_seminar = relationship("Subject", back_populates="seminar_subject")
    teacher_seminar = relationship("Teacher", back_populates="seminar_teacher")
    branch_seminar = relationship("Branch", back_populates="seminar_branch")
    school_seminar = relationship("School", back_populates="seminar_school")
    course_seminar = relationship("Course", back_populates="seminar_course")


# ed_staff_type 1= ประธาน , 2 = กรรมการ
# ed_status 0 = ยังสามารถแก้ไขได้ , 1 = ยืนยันการนำไปใช้


class ExamDate(Base):
    __tablename__ = 'app_exam_date'
    ed_id = Column(Integer, primary_key=True)
    ed_start_time = Column(Time)
    ed_end_time = Column(Time)
    ed_hour = Column(Float, nullable=False)
    ed_date = Column(Date)
    ed_ready = Column(Integer, default=0)
    ed_code = Column(String(128), nullable=False)
    active = Column(Integer, default=1)
    cancelled = Column(Integer, default=1)
    create_date = Column(DateTime)
    update_date = Column(DateTime)
    vehicle_type_id = Column(Integer, nullable=False)
    branch_id = Column(String(128), ForeignKey(
        "app_branch.branch_id", ondelete="CASCADE"))
    school_id = Column(String(128), ForeignKey(
        "app_school.school_id", ondelete="CASCADE"))

    branch_examdate = relationship("Branch", back_populates="examdate_branch")
    school_examdate = relationship("School", back_populates="examdate_school")
    regisetmain_tmp_examdate = relationship(
        "RegisterTmpMain", back_populates="examdate_regisetmain_tmp")
    regisetmain_core_examdate = relationship(
        "RegisterCoreMain", back_populates="examdate_regisetmain_core")


class ExamDateDirector(Base):
    __tablename__ = 'app_exam_date_director'
    edd_id = Column(Integer, primary_key=True)
    ed_code = Column(String(128), nullable=False)
    staff_exam_type = Column(Integer, nullable=False)
    teacher_id = Column(String(128), ForeignKey(
        "app_teacher.teacher_id", ondelete="CASCADE"))
    teacher_examdate_dt = relationship(
        "Teacher", back_populates="examdate_dt_teacher")


# rm_pay_status สถานะการชำระเงิน RS = Reservations (ลูกค้าจองตารางเรียน แต่ยังไม่ชำระเงิน) PP = Partial pay (ชำระเงินบางส่วนแต่ยังไม่ครบ) PA = Pay All (ชำระเงินครบทั้งหมดแล้ว)
# rm_status สถานะของการสมัครเรียน NR = New register สมัครเรียนเสร็จแล้ว ,LC = Learning Complete การเรียนครบชั่วโมงแล้ว , RT = Register Testing ลงทะเบียนสอบแล้ว
# rm_success  True คือเรียนจบหลักสูตร  , False เรียนไม่จบหลักสูตร  โดยถ้า course_group 1 สถานะ คือ RT จบหลักสูตร  นอกนั้น สถานะ LC คือจบหลักสูตร
# Table Register Tmp ชั่วคราว


class RegisterTmpMain(Base):
    __tablename__ = 'app_register_tmp_main'
    rm_id = Column(String(128), primary_key=True,
                   unique=True, default=generateId)
    rm_doc_number = Column(String(128), nullable=False)
    rm_pay_status = Column(String(128), nullable=False)
    rm_status = Column(String(128), nullable=False)
    rm_success = Column(Boolean, default=False)
    date_set = Column(Date)
    course_group = Column(Integer, nullable=False)
    create_date = Column(DateTime)
    update_date = Column(DateTime)
    vehicle_type_id = Column(Integer, nullable=False)
    course_id = Column(String(128), ForeignKey(
        "app_course.course_id", ondelete="CASCADE"))
    ed_id = Column(Integer, ForeignKey("app_exam_date.ed_id"))
    branch_id = Column(String(128), ForeignKey(
        "app_branch.branch_id", ondelete="CASCADE"))
    school_id = Column(String(128), ForeignKey(
        "app_school.school_id", ondelete="CASCADE"))

    course_regisetmain_tmp = relationship(
        "Course", back_populates="regisetmain_tmp_course")
    examdate_regisetmain_tmp = relationship(
        "ExamDate", back_populates="regisetmain_tmp_examdate")
    branch_regisetmain_tmp = relationship(
        "Branch", back_populates="regisetmain_tmp_branch")
    school_regisetmain_tmp = relationship(
        "School", back_populates="regisetmain_tmp_school")


class RegisterTmpCachSubject(Base):
    __tablename__ = 'app_register_tmp_cach_subject'
    rs_id = Column(String(128), primary_key=True,
                   unique=True, default=generateShortId)
    rs_hour_quota = Column(Float, nullable=False)
    rs_hour_use = Column(Float, nullable=False)
    rs_remark = Column(String(128), nullable=False)
    subject_id = Column(Integer, ForeignKey(
        "app_subject.subject_id", ondelete="CASCADE"))
    rm_id = Column(String(128), ForeignKey(
        "app_register_tmp_main.rm_id", ondelete="CASCADE"))


# rs_check สถานะตรวจรายวิชาว่าเรียนยัง value =1


class RegisterTmpSchedule(Base):
    __tablename__ = 'app_register_tmp_schedule'
    rs_id = Column(String(128), primary_key=True,
                   unique=True, default=generateShortId)
    subject_learn_type = Column(Integer, nullable=False)
    rs_start_time = Column(DateTime)
    rs_end_time = Column(DateTime)
    rs_hour = Column(Float, nullable=False)
    rs_check = Column(Boolean, default=False)
    create_date = Column(DateTime)
    update_date = Column(DateTime)
    subject_id = Column(Integer, ForeignKey(
        "app_subject.subject_id", ondelete="CASCADE"))
    teacher_id = Column(String(128), ForeignKey(
        "app_teacher.teacher_id", ondelete="CASCADE"))
    rm_id = Column(String(128), ForeignKey(
        "app_register_tmp_main.rm_id", ondelete="CASCADE"))
    branch_id = Column(String(128), ForeignKey(
        "app_branch.branch_id", ondelete="CASCADE"))
    school_id = Column(String(128), ForeignKey(
        "app_school.school_id", ondelete="CASCADE"))

    subject_rts = relationship("Subject", back_populates="rts_subject")
    teacher_rts = relationship("Teacher", back_populates="rts_teacher")


class RegisterTmpStudent(Base):
    __tablename__ = 'app_register_tmp_student'
    student_id = Column(String(128), primary_key=True,
                        unique=True, default=generateShortId)
    student_cover = Column(String(128), nullable=False)
    student_prefix = Column(String(128), nullable=False)
    student_firstname = Column(String(128), nullable=False)
    student_lastname = Column(String(128), nullable=False)
    student_id_number = Column(String(128), nullable=False)
    student_birthday = Column(Date)
    student_gender = Column(Integer, nullable=False)
    student_mobile = Column(String(128), nullable=False)
    student_email = Column(String(128), nullable=False)
    student_address = Column(String(128), nullable=False)
    create_date = Column(DateTime)
    update_date = Column(DateTime)
    location_id = Column(Integer, ForeignKey(
        "app_location_thai.location_id", ondelete="CASCADE"))
    country_id = Column(Integer, ForeignKey(
        "app_country.country_id", ondelete="CASCADE"))
    nationality_id = Column(Integer, ForeignKey(
        "app_country.country_id", ondelete="CASCADE"))
    rm_id = Column(String(128), ForeignKey(
        "app_register_tmp_main.rm_id", ondelete="CASCADE"))
    branch_id = Column(String(128), ForeignKey(
        "app_branch.branch_id", ondelete="CASCADE"))
    school_id = Column(String(128), ForeignKey(
        "app_school.school_id", ondelete="CASCADE"))

    student_tmp_location = relationship(
        "LocationThai", back_populates="location_student_tmp")


# Table Register หลัก
class RegisterCoreMain(Base):
    __tablename__ = 'app_register_core_main'
    rm_id = Column(String(128), primary_key=True,
                   unique=True, default=generateId)
    rm_doc_number = Column(String(128), nullable=False)
    rm_pay_status = Column(String(128), nullable=False)
    rm_status = Column(String(128), nullable=False)
    rm_success = Column(Boolean, default=False)
    date_set = Column(Date)
    course_group = Column(Integer, nullable=False)
    create_date = Column(DateTime)
    update_date = Column(DateTime)
    vehicle_type_id = Column(Integer, nullable=False)
    course_id = Column(String(128), ForeignKey(
        "app_course.course_id", ondelete="CASCADE"))
    ed_id = Column(Integer, ForeignKey(
        "app_exam_date.ed_id", ondelete="CASCADE"))
    branch_id = Column(String(128), ForeignKey(
        "app_branch.branch_id", ondelete="CASCADE"))
    school_id = Column(String(128), ForeignKey(
        "app_school.school_id", ondelete="CASCADE"))

    course_regisetmain_core = relationship(
        "Course", back_populates="regisetmain_core_course")
    examdate_regisetmain_core = relationship(
        "ExamDate", back_populates="regisetmain_core_examdate")
    branch_regisetmain_core = relationship(
        "Branch", back_populates="regisetmain_core_branch")
    school_regisetmain_core = relationship(
        "School", back_populates="regisetmain_core_school")
    student_register_core = relationship(
        "RegisterCoreStudent", back_populates="register_core_student")
    payment_rcm = relationship(
        "PaymentRegister", back_populates="rcm_payment", order_by='PaymentRegister.create_date')


class RegisterCoreCachSubject(Base):
    __tablename__ = 'app_register_core_cach_subject'
    rs_id = Column(String(128), primary_key=True,
                   unique=True, default=generateShortId)
    rs_hour_quota = Column(Float, nullable=False)
    rs_hour_use = Column(Float, nullable=False)
    rs_remark = Column(String(128), nullable=False)
    subject_id = Column(Integer, ForeignKey(
        "app_subject.subject_id", ondelete="CASCADE"))
    rm_id = Column(String(128), ForeignKey(
        "app_register_core_main.rm_id", ondelete="CASCADE"))
# rs_check สถานะตรวจรายวิชาว่าเรียนยัง value =1


class RegisterCoreSchedule(Base):
    __tablename__ = 'app_register_core_schedule'
    rs_id = Column(String(128), primary_key=True,
                   unique=True, default=generateShortId)
    subject_learn_type = Column(Integer, nullable=False)
    rs_start_time = Column(DateTime)
    rs_end_time = Column(DateTime)
    rs_hour = Column(Float, nullable=False)
    rs_check = Column(Boolean, default=False)
    create_date = Column(DateTime)
    update_date = Column(DateTime)
    subject_id = Column(Integer, ForeignKey(
        "app_subject.subject_id", ondelete="CASCADE"))
    teacher_id = Column(String(128), ForeignKey(
        "app_teacher.teacher_id", ondelete="CASCADE"))
    rm_id = Column(String(128), ForeignKey(
        "app_register_core_main.rm_id", ondelete="CASCADE"))
    branch_id = Column(String(128), ForeignKey(
        "app_branch.branch_id", ondelete="CASCADE"))
    school_id = Column(String(128), ForeignKey(
        "app_school.school_id", ondelete="CASCADE"))

    subject_rcs = relationship("Subject", back_populates="rcs_subject")
    teacher_rcs = relationship("Teacher", back_populates="rcs_teacher")


class RegisterCoreStudent(Base):
    __tablename__ = 'app_register_core_student'
    student_id = Column(String(128), primary_key=True,
                        unique=True, default=generateId)
    student_cover = Column(String(128), nullable=False)
    student_prefix = Column(String(128), nullable=False)
    student_firstname = Column(String(128), nullable=False)
    student_lastname = Column(String(128), nullable=False)
    student_id_number = Column(String(128), nullable=False)
    student_birthday = Column(Date)
    student_gender = Column(Integer, nullable=False)
    student_mobile = Column(String(128), nullable=False)
    student_email = Column(String(128), nullable=False)
    student_address = Column(String(128), nullable=False)
    create_date = Column(DateTime)
    update_date = Column(DateTime)
    location_id = Column(Integer, ForeignKey(
        "app_location_thai.location_id", ondelete="CASCADE"))
    country_id = Column(Integer, ForeignKey(
        "app_country.country_id", ondelete="CASCADE"))
    nationality_id = Column(Integer, ForeignKey(
        "app_country.country_id", ondelete="CASCADE"))
    rm_id = Column(String(128), ForeignKey(
        "app_register_core_main.rm_id", ondelete="CASCADE"))
    branch_id = Column(String(128), ForeignKey(
        "app_branch.branch_id", ondelete="CASCADE"))
    school_id = Column(String(128), ForeignKey(
        "app_school.school_id", ondelete="CASCADE"))

    student_core_location = relationship(
        "LocationThai", back_populates="location_student_core")
    register_core_student = relationship(
        "RegisterCoreMain", back_populates="student_register_core")


class PaymentRegister(Base):
    __tablename__ = 'app_payment_register'
    pr_id = Column(String(128), primary_key=True,
                   unique=True, default=generateId)
    pr_name = Column(String(128), nullable=False)
    pr_tax_number = Column(String(128), nullable=False)
    pr_address = Column(String(512), nullable=False)
    pr_number = Column(String(128), nullable=False)
    pr_discount_percent = Column(Float, nullable=False)
    pr_discount_amount = Column(Float, nullable=False)
    pr_total_amount = Column(Float, nullable=False)
    pr_pay = Column(Float, nullable=False)
    pr_debt = Column(Float, nullable=False)
    pr_remark = Column(String(256), nullable=False)
    pr_receipt_issuer = Column(String(256), nullable=False)
    pr_close_sale = Column(Boolean, default=False)
    create_date = Column(DateTime)
    update_date = Column(DateTime)
    rm_id = Column(String(128), ForeignKey(
        "app_register_core_main.rm_id", ondelete="CASCADE"))
    branch_id = Column(String(128), ForeignKey(
        "app_branch.branch_id", ondelete="CASCADE"))
    school_id = Column(String(128), ForeignKey(
        "app_school.school_id", ondelete="CASCADE"))
    rcm_payment = relationship(
        "RegisterCoreMain", back_populates="payment_rcm")
    payment_child = relationship(
        "PaymentRegisterList", back_populates="payment_parent")


class PaymentRegisterList(Base):
    __tablename__ = 'app_payment_register_list'
    pl_id = Column(Integer, primary_key=True)
    pl_name = Column(String(128), nullable=False)
    pl_unit = Column(Integer, nullable=False)
    pl_price_per_unit = Column(Float, nullable=False)
    pl_price_sum = Column(Float, nullable=False)
    pr_id = Column(String(128), ForeignKey(
        "app_payment_register.pr_id", ondelete="CASCADE"))

    payment_parent = relationship(
        "PaymentRegister", back_populates="payment_child")
