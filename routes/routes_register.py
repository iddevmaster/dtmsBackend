import calendar
from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, asc, desc, extract,  or_
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import func
from typing import Optional
from authen import auth_request
from data_common import base_branch_id, base_school_id
from database import get_db
from function import (ceil, datetimeSplit,
                      floattoint,  minusSecond,
                      noneToZero, plusSecond,
                      ternaryZero, time_difference, today, todaytime,
                      treeDigit)
from models import (Country, Course, CoursePrice, CourseWithSubject,
                    PaymentRegister, PaymentRegisterList, RegisterCoreMain,
                    RegisterCoreSchedule, RegisterCoreStudent, RegisterTmpMain,
                    RegisterTmpSchedule, RegisterTmpStudent,
                    RegisterTmpCachSubject, Subject, Teacher, TeacherLicense, RegisterCoreCachSubject)

from schemas_format.general_schemas import (FilterRequestSchema, fullcalendarTypeAOutSchema, fullcalendarTypeBOutSchema,
                                            ResponseData, ResponseProcess)

from schemas_format.register_schemas import SearchScheduleInSchema, PaymentRegisterInSchema, RegisterScheduleInSchema, RegisterScheduleInUpdateSchema, RegisterStudentInSchema
now = datetime.now()  # current date and time
year = now.strftime("%Y")
month = now.strftime("%m")
c = calendar.Calendar()

router_register = APIRouter()


@router_register.post("/search_schedule", name="ค้นหาตารางเรียน")
async def search_schedule(request: SearchScheduleInSchema, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    course_id = request.course_id
    _course = db.query(Course).filter(
        Course.course_id == course_id).one_or_none()
    if not _course:
        raise HTTPException(status_code=404, detail="Data not found")
    vehicle_type_id = _course.vehicle_type_id
    _teacher = db.query(Teacher).join(TeacherLicense, Teacher.teacher_id == TeacherLicense.teacher_id).order_by(desc(Teacher.create_date)).filter(
        Teacher.branch_id == request.branch_id,  Teacher.cancelled == 1, TeacherLicense.vehicle_type_id == vehicle_type_id).all()
    [year, month, day] = str(request.date_set).split("-")

    obj = []
    for dateRow in c.itermonthdates(int(year), int(month)):
        # print(date)
        start = str(dateRow) + " " + str(request.start_time)
        end = str(dateRow) + " " + str(request.end_time)
        # print(start)
        for row in _teacher:
            # chkteacherSchedule = db.query(RegisterTmpSchedule).filter(
            #     and_(func.date(RegisterTmpSchedule.rs_start_time) >= dateRow,
            #          func.date(RegisterTmpSchedule.rs_end_time) <= dateRow),
            #     RegisterTmpSchedule.teacher_id == row.teacher_id
            # ).count()
            chkteacherTmpSchedule = db.query(RegisterTmpSchedule).filter(
                RegisterTmpSchedule.rs_start_time.between(start, end),
                RegisterTmpSchedule.rs_end_time.between(start, end),
                RegisterTmpSchedule.teacher_id == row.teacher_id
            ).count()
            chkteacherMainSchedule = db.query(RegisterCoreSchedule).filter(
                RegisterCoreSchedule.rs_start_time.between(start, end),
                RegisterCoreSchedule.rs_end_time.between(start, end),
                RegisterCoreSchedule.teacher_id == row.teacher_id
            ).count()

            if chkteacherTmpSchedule <= 0 and chkteacherMainSchedule <= 0:
                content = fullcalendarTypeBOutSchema(
                    id=row.teacher_id,
                    title=str(row.teacher_firstname) + " " +
                    str(row.teacher_lastname),
                    start=dateRow,
                    end=dateRow,
                    backgroundColor="#c40048"
                )
                obj.append(content)
    _register = RegisterTmpMain(
        rm_doc_number="-",
        rm_pay_status="RS",
        rm_status="NR",
        date_set=request.date_set,
        course_group=_course.course_group,
        create_date=todaytime(),
        update_date=todaytime(),
        vehicle_type_id=vehicle_type_id,
        course_id=request.course_id,
        ed_id=1,
        branch_id=request.branch_id,
        school_id=request.school_id
    )
    db.add(_register)
    db.commit()
    db.refresh(_register)
    rm_id = _register.rm_id

    # กำหนดรายวิชาปฏิบัติชั่วคราว
    _subject = db.query(CourseWithSubject).order_by(asc(CourseWithSubject.subject_id)).filter(
        CourseWithSubject.course_id == course_id, CourseWithSubject.subject_learn_type == 2).all()
    for row in _subject:
        remark_title = str(row.subject_coursewithsubject.subject_code) + \
            " " + str(row.subject_coursewithsubject.subject_name)
        _catch = RegisterTmpCachSubject(
            rs_hour_quota=row.learn_time,
            rs_hour_use=row.learn_time,
            rs_remark=remark_title,
            rm_id=rm_id,
            subject_id=row.subject_id,
        )
        db.add(_catch)
        db.commit()
    return {"rm_id": rm_id, "course_group": _course.course_group, "vehicle_type_id": _course.vehicle_type_id, "teacher_list": obj}


@router_register.get("/update_exam_tmp/{rm_id}/{ed_id}", name="แก้ไขวันสอบจากข้อมูลชั่วคราว")
async def update_exam_tmp(rm_id: str, ed_id: int, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _register = db.query(RegisterTmpMain).filter(
        RegisterTmpMain.rm_id == rm_id).one_or_none()
    if not _register:
        raise HTTPException(status_code=404, detail="Data not found")
    _register.ed_id = ed_id
    db.commit()
    return ResponseProcess(status="success", status_code="200", message="Success update data")


@router_register.get("/check/{rm_id}")
def register_check(rm_id: str,  db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _register = db.query(RegisterTmpMain).filter(
        RegisterTmpMain.rm_id == rm_id).options(joinedload(RegisterTmpMain.course_regisetmain_tmp), joinedload(RegisterTmpMain.branch_regisetmain_tmp)).one_or_none()
    if not _register:
        raise HTTPException(status_code=404, detail="Data not found")
    return _register


@router_register.get("/subject_catch/{rm_id}", name="รายวิชาปฏิบัติชั่วคราว")
async def get_subject_catch(rm_id: str,  db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _subject = db.query(RegisterTmpCachSubject).order_by(asc(RegisterTmpCachSubject.subject_id)).filter(
        RegisterTmpCachSubject.rm_id == rm_id, RegisterTmpCachSubject.rs_hour_use > 0).all()
    return _subject


@router_register.post("/create_schedule_tmp", name="บันทึกรายวิชาลงในปฏิทินชั่วคราว")
async def create_schedule_tmp(request: RegisterScheduleInSchema, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    rm_id = request.rm_id
    subject_learn_type = request.subject_learn_type
    _data = db.query(RegisterTmpMain).filter(
        RegisterTmpMain.rm_id == rm_id).one_or_none()
    if not _data:
        raise HTTPException(status_code=404, detail="Data not found")

    vehicle_type_id = _data.vehicle_type_id
    rs_start_time = request.rs_start_time
    rs_end_time = request.rs_end_time

    teacher_id = request.teacher_id
    # print(rs_start_time)
    # ลบออก 1 วิ เพื่อใช้คำสั่ง between เวลาต่อเนื่องได้
    datestart, timestart = datetimeSplit(rs_start_time, 1)
    dateend, timeend = datetimeSplit(rs_end_time, 1)
    newtimestart = str(datestart) + " " + plusSecond(timestart, 1)
    newtimeend = str(dateend) + " " + minusSecond(timeend, 1)
    hourstart = datetimeSplit(rs_start_time, 3)[0]
    hourend = datetimeSplit(rs_end_time, 3)[0]

    # ปรับปรุงวันที่ค้นหา
    _data.date_set = datestart
    _data.update_date = todaytime()
    db.commit()
    # คำนวนชั่วโมง
    rs_hour = time_difference(
        timestart, timeend)

    # ตรวจสอบว่าตารางเรียนซ้ำกันหรือไม่
    chkteacherTmpSchedule = db.query(RegisterTmpSchedule).filter(
        func.date(RegisterTmpSchedule.rs_start_time) == datestart,
        or_(RegisterTmpSchedule.rs_start_time.between(newtimestart, newtimeend),
            RegisterTmpSchedule.rs_end_time.between(newtimestart, newtimeend),
            and_(extract('hour', RegisterTmpSchedule.rs_start_time) <= int(hourstart),
            extract('hour', RegisterTmpSchedule.rs_end_time) >= int(hourend))
            ),
        RegisterTmpSchedule.teacher_id == teacher_id,
        RegisterTmpSchedule.subject_learn_type == subject_learn_type
    ).count()
    chkteacherMainSchedule = db.query(RegisterCoreSchedule).filter(
        func.date(RegisterCoreSchedule.rs_start_time) == datestart,
        or_(RegisterCoreSchedule.rs_start_time.between(newtimestart, newtimeend),
            RegisterCoreSchedule.rs_end_time.between(newtimestart, newtimeend),
            and_(extract('hour', RegisterCoreSchedule.rs_start_time) <= int(hourstart),
            extract('hour', RegisterCoreSchedule.rs_end_time) >= int(hourend))
            ),
        RegisterCoreSchedule.teacher_id == teacher_id,
        RegisterCoreSchedule.subject_learn_type == subject_learn_type
    ).count()
    # print(chkteacherMainSchedule)
    # ถ้าเป็นรถยนต์ไม่สามารถให้ซ้อนซ้ำกันได้
    if chkteacherTmpSchedule > 0 and vehicle_type_id == 1:
        raise HTTPException(status_code=404, detail="Data not found")
    if chkteacherMainSchedule > 0 and vehicle_type_id == 1:
        raise HTTPException(status_code=404, detail="Data not found")
    # คำนวนชั่วโมงรายวิชาที่บันทึกไปแล้ว
    get_sum_hour = db.query(func.sum(RegisterTmpSchedule.rs_hour).label('sum_hour')).filter(
        RegisterTmpSchedule.subject_id == request.subject_id, RegisterTmpSchedule.rm_id == rm_id,
        RegisterTmpSchedule.subject_learn_type == subject_learn_type).first()
    sum_hour = noneToZero(get_sum_hour.sum_hour) + float(rs_hour)
    _subject = db.query(RegisterTmpCachSubject).filter(
        RegisterTmpCachSubject.subject_id == request.subject_id, RegisterTmpCachSubject.rm_id == rm_id).one_or_none()
    if _subject:
        # ถ้าชั่วโมงที่บันทึกมากกว่า โควดต้าชั่วโมงที่กำหนด
        if sum_hour > _subject.rs_hour_quota:
            raise HTTPException(status_code=404, detail="Data not found")

        calHour = float(_subject.rs_hour_quota) - \
            float(sum_hour)
        _subject.rs_hour_use = calHour
        db.commit()

    _register = RegisterTmpSchedule(
        subject_learn_type=subject_learn_type,
        rs_start_time=rs_start_time,
        rs_end_time=rs_end_time,
        rs_hour=rs_hour,
        create_date=todaytime(),
        update_date=todaytime(),
        subject_id=request.subject_id,
        teacher_id=teacher_id,
        rm_id=rm_id,
        branch_id=request.branch_id,
        school_id=request.school_id
    )
    db.add(_register)
    db.commit()

    return ResponseProcess(status="success", status_code="200",  message="Success Create data")


@router_register.post("/create_schedule_tmp_multiple", name="บันทึกรายวิชาลงในปฏิทินชั่วคราวแบบหลายวิชาพร้อมกัน")
async def create_schedule_tmp_multiple(request: list[RegisterScheduleInSchema], db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    rm_id = request[0].rm_id

    _data = db.query(RegisterTmpMain).filter(
        RegisterTmpMain.rm_id == rm_id).one_or_none()
    if not _data:
        raise HTTPException(status_code=404, detail="Data not found")
    obj = []
    for row in request:
        timestart = datetimeSplit(row.rs_start_time, 1)[1]
        timeend = datetimeSplit(row.rs_end_time, 1)[1]
        rs_hour = time_difference(
            timestart, timeend)
        _register = RegisterTmpSchedule(
            subject_learn_type=row.subject_learn_type,
            rs_start_time=row.rs_start_time,
            rs_end_time=row.rs_end_time,
            rs_hour=rs_hour,
            create_date=todaytime(),
            update_date=todaytime(),
            subject_id=row.subject_id,
            teacher_id=row.teacher_id,
            rm_id=rm_id,
            branch_id=row.branch_id,
            school_id=row.school_id
        )
        obj.append(_register)
    db.add_all(obj)
    db.commit()
    return ResponseProcess(status="success", status_code="200",  message="Success Create data")


@router_register.put("/update_schedule_tmp/{rs_id}", name="แก้ไขรายวิชาลงในปฏิทินชั่วคราว")
async def update_schedule_tmp(rs_id: str, request: RegisterScheduleInUpdateSchema, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _register = db.query(RegisterTmpSchedule).filter(
        RegisterTmpSchedule.rs_id == rs_id).one_or_none()
    if not _register:
        raise HTTPException(status_code=404, detail="Data not found")

    rm_id = _register.rm_id
    _data = db.query(RegisterTmpMain).filter(
        RegisterTmpMain.rm_id == rm_id).one_or_none()
    vehicle_type_id = _data.vehicle_type_id
    rs_start_time = request.rs_start_time
    rs_end_time = request.rs_end_time
    teacher_id = _register.teacher_id
    subject_learn_type = _register.subject_learn_type
    # ลบออก 1 วิ เพื่อใช้คำสั่ง between เวลาต่อเนื่องได้
    datestart, timestart = datetimeSplit(rs_start_time, 1)
    dateend, timeend = datetimeSplit(rs_end_time, 1)
    newtimestart = str(datestart) + " " + plusSecond(timestart, 1)
    newtimeend = str(dateend) + " " + minusSecond(timeend, 1)

    hourstart = datetimeSplit(rs_start_time, 3)[0]
    hourend = datetimeSplit(rs_end_time, 3)[0]
    # print(hourstart)
    # ตรวจสอบว่าตารางเรียนซ้ำกันหรือไม่
    chkteacherTmpSchedule = db.query(RegisterTmpSchedule).filter(
        func.date(RegisterTmpSchedule.rs_start_time) == datestart,
        or_(RegisterTmpSchedule.rs_start_time.between(newtimestart, newtimeend),
            RegisterTmpSchedule.rs_end_time.between(newtimestart, newtimeend),
            and_(extract('hour', RegisterTmpSchedule.rs_start_time) <= int(hourstart),
            extract('hour', RegisterTmpSchedule.rs_end_time) >= int(hourend))
            ),

        RegisterTmpSchedule.teacher_id == teacher_id,
        RegisterTmpSchedule.rs_id != rs_id,
        RegisterTmpSchedule.subject_learn_type == subject_learn_type
    ).count()
    chkteacherMainSchedule = db.query(RegisterCoreSchedule).filter(
        func.date(RegisterCoreSchedule.rs_start_time) == datestart,
        or_(RegisterCoreSchedule.rs_start_time.between(newtimestart, newtimeend),
            RegisterCoreSchedule.rs_end_time.between(newtimestart, newtimeend),
            and_(extract('hour', RegisterCoreSchedule.rs_start_time) <= int(hourstart),
            extract('hour', RegisterCoreSchedule.rs_end_time) >= int(hourend))
            ),
        RegisterCoreSchedule.teacher_id == teacher_id,
        RegisterCoreSchedule.subject_learn_type == subject_learn_type
    ).count()

    # ถ้าเป็นรถยนต์ไม่สามารถให้ซ้อนซ้ำกันได้
    if chkteacherTmpSchedule > 0 and vehicle_type_id == 1:
        raise HTTPException(status_code=404, detail="Data not found")
    if chkteacherMainSchedule > 0 and vehicle_type_id == 1:
        raise HTTPException(status_code=404, detail="Data not found")

    subject_id = _register.subject_id

    # คำนวนชั่วโมง
    rs_hour = time_difference(
        timestart, timeend)

    # คำนวนชั่วโมงรายวิชาที่บันทึกไปแล้ว
    get_sum_hour = db.query(func.sum(RegisterTmpSchedule.rs_hour).label('sum_hour')).filter(
        RegisterTmpSchedule.rs_id != rs_id, RegisterTmpSchedule.subject_id == subject_id, RegisterTmpSchedule.rm_id == rm_id,
        RegisterTmpSchedule.subject_learn_type == subject_learn_type).first()
    sum_hour = noneToZero(get_sum_hour.sum_hour) + float(rs_hour)

    _subject = db.query(RegisterTmpCachSubject).filter(
        RegisterTmpCachSubject.subject_id == subject_id, RegisterTmpCachSubject.rm_id == rm_id).one_or_none()
    if _subject:
        # ถ้าชั่วโมงที่บันทึกมากกว่า โควต้าชั่วโมงที่กำหนด
        if sum_hour > _subject.rs_hour_quota:

            raise HTTPException(status_code=404, detail="Data not found")
        calHour = float(_subject.rs_hour_quota) - \
            float(sum_hour)
        _subject.rs_hour_use = calHour
        db.commit()

    _register.rs_start_time = rs_start_time
    _register.rs_end_time = rs_end_time
    _register.rs_hour = rs_hour
    db.commit()

    # debug = str(sum_hour) + " " + str(_subject.rs_hour_quota)

    return ResponseProcess(status="success", status_code="200", message="Success Update data")


@router_register.get("/subject_schedule_tmp/{rm_id}", name="ปฏิทินการสอนปฏิบัติของครูทั้งหมดอ้างอิงข้อมูลชั่วคราว")
async def get_schedule_tmp(rm_id: str, teacher_id: str, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _data = db.query(RegisterTmpMain).filter(
        RegisterTmpMain.rm_id == rm_id).first()
    if not _data:
        raise HTTPException(status_code=404, detail="Data not found")
    obj = []
    year, month, day = datetimeSplit(str(_data.date_set) + " 00:00:00", 2)
    _register = db.query(RegisterTmpSchedule).filter(
        RegisterTmpSchedule.rm_id == rm_id,
        RegisterTmpSchedule.subject_learn_type == 2).all()
    _register_tmp = db.query(RegisterTmpSchedule).filter(
        extract('month', RegisterTmpSchedule.rs_start_time) == month,
        extract('year', RegisterTmpSchedule.rs_start_time) == year,
        RegisterTmpSchedule.teacher_id == teacher_id,
        RegisterTmpSchedule.rm_id != rm_id,
        RegisterTmpSchedule.subject_learn_type == 2
    ).all()
    _register_main = db.query(RegisterCoreSchedule).filter(
        extract('month', RegisterCoreSchedule.rs_start_time) == month,
        extract('year', RegisterCoreSchedule.rs_start_time) == year,
        RegisterCoreSchedule.teacher_id == teacher_id,
        RegisterCoreSchedule.subject_learn_type == 2
    ).all()
    if _register:
        for row in _register:
            content = fullcalendarTypeAOutSchema(
                id=row.rs_id,
                title="(" + str(floattoint(row.rs_hour)) + ") " +
                str(row.subject_rts.subject_name),
                start=row.rs_start_time,
                end=row.rs_end_time,
                editable=True,
                backgroundColor=""
            )
            obj.append(content)
    if _register_tmp:
        for row1 in _register_tmp:

            content1 = fullcalendarTypeAOutSchema(
                title="(" + str(floattoint(row1.rs_hour)) + ") " +
                str(row1.subject_rts.subject_name),
                start=row1.rs_start_time,
                end=row1.rs_end_time,
                editable=False,
                backgroundColor="#f5ab16"
            )

            obj.append(content1)
    if _register_main:
        for row2 in _register_main:
            content2 = fullcalendarTypeAOutSchema(
                title="(" + str(floattoint(row2.rs_hour)) + ") " +
                str(row2.subject_rcs.subject_name),
                start=row2.rs_start_time,
                end=row2.rs_end_time,
                editable=False,
                backgroundColor="#33d406"
            )
            obj.append(content2)
    return obj


@router_register.delete("/subject_schedule_tmp/{rs_id}", name="ลบรายวิชาชั่วคราวจากปฏิทินการสอน")
async def delete_schedule_tmp(rs_id: str, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _register = db.query(RegisterTmpSchedule).filter(
        RegisterTmpSchedule.rs_id == rs_id).one_or_none()
    if not _register:
        raise HTTPException(status_code=404, detail="Data not found")
    rs_hour = _register.rs_hour
    subject_id = _register.subject_id
    rm_id = _register.rm_id
    db.delete(_register)
    db.commit()
    # คืนเวลาที่พึ่งลบไป
    _subject = db.query(RegisterTmpCachSubject).filter(
        RegisterTmpCachSubject.subject_id == subject_id, RegisterTmpCachSubject.rm_id == rm_id).one_or_none()
    calHour = float(_subject.rs_hour_use) + float(rs_hour)
    _subject.rs_hour_use = calHour
    db.commit()
    return ResponseProcess(status="success", status_code="200", message="Success delete data")


@router_register.delete("/subject_schedule_tmp/multiple/{subject_learn_type}/{rm_id}", name="ลบตารางเรียนตามประเภทรายวิชาทั้งหมด")
async def delete_schedule_multiple(subject_learn_type: int, rm_id: str, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _register = db.query(RegisterTmpSchedule).filter(
        RegisterTmpSchedule.subject_learn_type == subject_learn_type, RegisterTmpSchedule.rm_id == rm_id).all()
    if not _register:
        raise HTTPException(status_code=404, detail="Data not found")
    # Delete multiple records
    db.query(RegisterTmpSchedule).filter(
        RegisterTmpSchedule.subject_learn_type == subject_learn_type, RegisterTmpSchedule.rm_id == rm_id).delete()
    db.commit()
    return ResponseProcess(status="success", status_code="200", message="Success delete data")


@router_register.post("/student_tmp", name="บันทึกข้อมูลนักเรียนชั่วคราว")
async def create_student_tmp(request: RegisterStudentInSchema, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    rm_id = request.rm_id
    _student = db.query(RegisterTmpStudent).filter(
        RegisterTmpStudent.rm_id == rm_id).one_or_none()
    if not _student:
        _register = RegisterTmpStudent(
            student_cover=request.student_cover,
            student_prefix=request.student_prefix,
            student_firstname=request.student_firstname,
            student_lastname=request.student_lastname,
            student_id_number=request.student_id_number,
            student_birthday=request.student_birthday,
            student_gender=request.student_gender,
            student_mobile=request.student_mobile,
            student_email=request.student_email,
            student_address=request.student_address,
            create_date=todaytime(),
            update_date=todaytime(),
            location_id=request.location_id,
            country_id=request.country_id,
            nationality_id=request.nationality_id,
            rm_id=request.rm_id,
            branch_id=request.branch_id,
            school_id=request.school_id
        )
        db.add(_register)
    else:
        _student.student_cover = request.student_cover
        _student.student_prefix = request.student_prefix,
        _student.student_firstname = request.student_firstname
        _student.student_lastname = request.student_lastname
        _student.student_id_number = request.student_id_number
        _student.student_birthday = request.student_birthday
        _student.student_gender = request.student_gender,
        _student.student_mobile = request.student_mobile
        _student.student_email = request.student_email
        _student.student_address = request.student_address
        _student.update_date = todaytime(),
        _student.location_id = request.location_id
        _student.country_id = request.country_id
        _student.nationality_id = request.nationality_id
        _student.branch_id = request.branch_id
        _student.school_id = request.school_id
    db.commit()
    return ResponseProcess(status="success", status_code="200", message="Success created data")


@router_register.get("/student_tmp/{rm_id}", name="ข้อมูลนักเรียนชั่วคราว")
async def get_student_tmp(rm_id: str,  db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _student = db.query(RegisterTmpStudent).filter(
        RegisterTmpStudent.rm_id == rm_id).options(joinedload(RegisterTmpStudent.student_tmp_location)).one_or_none()
    if not _student:
        raise HTTPException(status_code=404, detail="Data not found")
    _country = db.query(Country).filter(
        Country.country_id == _student.country_id).one_or_none()
    _nationality = db.query(Country).filter(
        Country.country_id == _student.nationality_id).one_or_none()
    _student.country_id = [_country]
    _student.nationality_id = [_nationality]
    db.add_all([_student])
    db.commit
    return _student


@router_register.get("/result/{rm_id}", name="ข้อมูลการสมัครก่อนการบันทึก")
async def register_result(rm_id: str,  db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _main = db.query(RegisterTmpMain).options(joinedload(RegisterTmpMain.course_regisetmain_tmp),
                                              joinedload(
                                                  RegisterTmpMain.examdate_regisetmain_tmp),
                                              joinedload(
                                                  RegisterTmpMain.branch_regisetmain_tmp),
                                              joinedload(RegisterTmpMain.school_regisetmain_tmp)).filter(
        RegisterTmpMain.rm_id == rm_id).one_or_none()
    if not _main:
        raise HTTPException(status_code=404, detail="Data not found")
    _student = db.query(RegisterTmpStudent).filter(
        RegisterTmpStudent.rm_id == rm_id).options(joinedload(RegisterTmpStudent.student_tmp_location)).one_or_none()
    _country = db.query(Country).filter(
        Country.country_id == _student.country_id).one_or_none()
    _nationality = db.query(Country).filter(
        Country.country_id == _student.nationality_id).one_or_none()
    _student.country_id = [_country]
    _student.nationality_id = [_nationality]
    db.add_all([_student])
    db.commit
    _schedule = db.query(RegisterTmpSchedule).options(joinedload(RegisterTmpSchedule.subject_rts), joinedload(RegisterTmpSchedule.teacher_rts)).order_by(asc(RegisterTmpSchedule.subject_learn_type), asc(RegisterTmpSchedule.rs_start_time)).filter(
        RegisterTmpSchedule.rm_id == rm_id).all()
    return {"main": _main, "student": _student, "schedule": _schedule}


@router_register.get("/save/{rm_id}", name="บันทึกข้อมูลการสมัครเรียน")
async def save_register(rm_id: str,  db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _main = db.query(RegisterTmpMain).filter(
        RegisterTmpMain.rm_id == rm_id).one_or_none()
    _student = db.query(RegisterTmpStudent).filter(
        RegisterTmpStudent.rm_id == rm_id).one_or_none()
    _schedule = db.query(RegisterTmpSchedule).filter(
        RegisterTmpSchedule.rm_id == rm_id).all()
    _cach_subject = db.query(RegisterTmpCachSubject).filter(
        RegisterTmpCachSubject.rm_id == rm_id).all()
    if not _main:
        raise HTTPException(status_code=404, detail="Data not found")
    new_rm_id = None
    if _main:
        d = today()
        total_data = db.query(RegisterCoreMain).filter(
            func.date(RegisterCoreMain.create_date) == d,
            RegisterCoreMain.branch_id == _main.branch_id).count()
        [year, month, day] = str(d).split("-")
        doc_number = year+month+day + treeDigit(total_data+1)
        branch_id = _main.branch_id
        school_id = _main.school_id
        rm_doc_number = "R" + str(branch_id[0:3]) + \
            str(school_id[0:3]) + str(doc_number)
        # บันทึกตารางสมัครหลัก
        _save_main = RegisterCoreMain(
            rm_doc_number=rm_doc_number,
            rm_pay_status=_main.rm_pay_status,
            rm_status=_main.rm_status,
            date_set=_main.date_set,
            course_group=_main.course_group,
            create_date=_main.create_date,
            update_date=_main.update_date,
            course_id=_main.course_id,
            vehicle_type_id=_main.vehicle_type_id,
            ed_id=_main.ed_id,
            branch_id=_main.branch_id,
            school_id=_main.school_id,
        )
        db.add(_save_main)
        db.commit()
        db.refresh(_save_main)
        new_rm_id = _save_main.rm_id
    if _student and new_rm_id is not None:
        # บันทึกข้อมูลนักเรียน
        _save_student = RegisterCoreStudent(
            student_cover=_student.student_cover,
            student_prefix=_student.student_prefix,
            student_firstname=_student.student_firstname,
            student_lastname=_student.student_lastname,
            student_id_number=_student.student_id_number,
            student_birthday=_student.student_birthday,
            student_gender=_student.student_gender,
            student_mobile=_student.student_mobile,
            student_email=_student.student_email,
            student_address=_student.student_address,
            create_date=_student.create_date,
            update_date=_student.update_date,
            location_id=_student.location_id,
            country_id=_student.country_id,
            nationality_id=_student.nationality_id,
            rm_id=new_rm_id,
            branch_id=_student.branch_id,
            school_id=_student.school_id,
        )
        db.add(_save_student)
        db.commit()
    # บันทึกตารางเรียน
    obj = []
    if _schedule and new_rm_id is not None:
        for row in _schedule:
            _save_schedule = RegisterCoreSchedule(
                subject_learn_type=row.subject_learn_type,
                rs_start_time=row.rs_start_time,
                rs_end_time=row.rs_end_time,
                rs_hour=row.rs_hour,
                rs_check=row.rs_check,
                create_date=row.create_date,
                update_date=row.update_date,
                subject_id=row.subject_id,
                teacher_id=row.teacher_id,
                rm_id=new_rm_id,
                branch_id=row.branch_id,
                school_id=row.school_id
            )
            obj.append(_save_schedule)
    db.add_all(obj)
    db.commit()
    # บันทึก catch รายวิชาปฏิบัติ
    obj1 = []
    if _cach_subject and new_rm_id is not None:
        for row in _cach_subject:
            _save_cach_subject = RegisterCoreCachSubject(
                rs_hour_quota=row.rs_hour_quota,
                rs_hour_use=row.rs_hour_use,
                rs_remark=row.rs_remark,
                subject_id=row.subject_id,
                rm_id=new_rm_id,
            )
            obj1.append(_save_cach_subject)
    db.add_all(obj1)
    db.commit()
    return {"rm_id": new_rm_id}


@router_register.get("/result/core/{rm_id}", name="ข้อมูลการสมัครหลังการบันทึก")
async def register_core_result(rm_id: str,  db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _main = db.query(RegisterCoreMain).options(joinedload(RegisterCoreMain.course_regisetmain_core),
                                               joinedload(
        RegisterCoreMain.examdate_regisetmain_core),
        joinedload(
        RegisterCoreMain.branch_regisetmain_core),
        joinedload(RegisterCoreMain.school_regisetmain_core)).filter(
        RegisterCoreMain.rm_id == rm_id).one_or_none()
    if not _main:
        raise HTTPException(status_code=404, detail="Data not found")
    _student = db.query(RegisterCoreStudent).filter(
        RegisterCoreStudent.rm_id == rm_id).options(joinedload(RegisterCoreStudent.student_core_location)).one_or_none()
    _country = db.query(Country).filter(
        Country.country_id == _student.country_id).one_or_none()
    _nationality = db.query(Country).filter(
        Country.country_id == _student.nationality_id).one_or_none()
    _course_price = db.query(CoursePrice).filter(
        CoursePrice.course_id == _main.course_id, CoursePrice.branch_id == _main.branch_id).first()
    _subject_cach = db.query(RegisterCoreCachSubject).order_by(asc(RegisterCoreCachSubject.subject_id)).filter(
        RegisterCoreCachSubject.rm_id == rm_id, RegisterCoreCachSubject.rs_hour_use > 0).all()
    price = 0
    if _course_price:
        price = _course_price.cp_price

    _student.country_id = [_country]
    _student.nationality_id = [_nationality]
    db.add_all([_student])
    db.commit
    _schedule = db.query(RegisterCoreSchedule).options(joinedload(RegisterCoreSchedule.subject_rcs), joinedload(RegisterCoreSchedule.teacher_rcs)).order_by(asc(RegisterCoreSchedule.subject_learn_type), asc(RegisterCoreSchedule.rs_start_time)).filter(
        RegisterCoreSchedule.rm_id == rm_id).all()
    _payment = db.query(PaymentRegister).order_by(desc(PaymentRegister.create_date)).filter(
        PaymentRegister.rm_id == rm_id).options(joinedload(PaymentRegister.payment_child)).all()

    return {"main": _main, "student": _student, "schedule": _schedule, "course_price": price, "payment": _payment, "subject_cach": _subject_cach}


@router_register.delete("/emptycode/{rm_id}", name="ทำความสะอาดแคช โดยแยก rm_id หรือ all ทั้งหมด")
async def emptycode(rm_id: str, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    if rm_id == "all":
        db.query(RegisterTmpMain).delete()
        db.commit()
    else:
        db.query(RegisterTmpMain).filter(
            RegisterTmpMain.rm_id == rm_id).delete()
        db.commit()
    return ResponseProcess(status="success", status_code="200", message="Success delete data")


@router_register.post("/payment", name="บันทึกรายการชำระเงิน")
async def save_payment(request: PaymentRegisterInSchema,  db: Session = Depends(get_db),  authenticated: bool = Depends(auth_request)):
    _register = db.query(RegisterCoreMain).filter(
        RegisterCoreMain.rm_id == request.rm_id).one_or_none()
    if not _register:
        raise HTTPException(status_code=404, detail="Data not found")
    d = today()
    total_data = db.query(PaymentRegister).filter(
        func.date(PaymentRegister.create_date) == d,
        PaymentRegister.branch_id == _register.branch_id).count()
    [year, month, day] = str(d).split("-")
    doc_number = year+month+day + treeDigit(total_data+1)
    branch_id = _register.branch_id
    school_id = _register.school_id
    pr_number = "P" + str(branch_id[0:3]) + \
        str(school_id[0:3]) + str(doc_number)
    pr_debt = request.pr_debt
    rm_id = request.rm_id
    if pr_debt > 0:
        rm_pay_status = "PP"
    else:
        rm_pay_status = "PA"
    # ปรับสถานะการชำระเงิน
    _register = db.query(RegisterCoreMain).filter(
        RegisterCoreMain.rm_id == rm_id).one_or_none()
    _register.rm_pay_status = rm_pay_status
    db.commit()
    # ข้อมูลชำระเงินหลัก
    _save_main = PaymentRegister(
        pr_name=request.pr_name,
        pr_tax_number=request.pr_tax_number,
        pr_address=request.pr_address,
        pr_number=pr_number,
        pr_discount_percent=request.pr_discount_percent,
        pr_discount_amount=request.pr_discount_amount,
        pr_total_amount=request.pr_total_amount,
        pr_pay=request.pr_pay,
        pr_debt=pr_debt,
        pr_remark=request.pr_remark,
        pr_receipt_issuer=request.pr_receipt_issuer,
        rm_id=rm_id,
        create_date=todaytime(),
        update_date=todaytime(),
        branch_id=branch_id,
        school_id=school_id,
    )
    db.add(_save_main)
    db.commit()
    db.refresh(_save_main)
    # รายการที่ต้องชำระ
    pr_id = _save_main.pr_id
    for row in request.line:
        _save_list = PaymentRegisterList(
            pl_name=row.pl_name,
            pl_unit=row.pl_unit,
            pl_price_per_unit=row.pl_price_per_unit,
            pl_price_sum=row.pl_price_sum,
            pr_id=pr_id
        )
        db.add(_save_list)
        db.commit()
    return ResponseProcess(status="success", status_code="200", message="Success Create data")
# https://phyblas.hinaboshi.com/20200529


@router_register.post("/list/{school_id}", name="ทะเบียนรายการสมัครทั้งหมดโดยแยกตามรหัสโรงเรียนและสาขา")
async def register_list(request: FilterRequestSchema, school_id: str, branch_id: str = "all",   db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    skip = ternaryZero(((request.page - 1) * request.per_page))
    limit = request.per_page
    search_value = request.search_value
    if branch_id != 'all':
        # โชว์ครูเฉพาะสาขาตนเอง
        queryset = RegisterCoreMain.branch_id == branch_id
    else:
        queryset = RegisterCoreMain.school_id == school_id
    searchFilter = or_(RegisterCoreStudent.student_firstname.contains(search_value),
                       RegisterCoreStudent.student_lastname.contains(
                           search_value),
                       RegisterCoreStudent.student_id_number.contains(
                           search_value),
                       RegisterCoreStudent.student_mobile.contains(
                           search_value),
                       RegisterCoreMain.rm_doc_number.contains(search_value))

    if search_value:
        result = db.query(RegisterCoreMain).order_by(desc(RegisterCoreMain.create_date)).join(RegisterCoreStudent, RegisterCoreMain.rm_id == RegisterCoreStudent.rm_id).filter(
            queryset, searchFilter).options(joinedload(RegisterCoreMain.student_register_core), joinedload(RegisterCoreMain.course_regisetmain_core), joinedload(RegisterCoreMain.branch_regisetmain_core)).offset(skip).limit(limit).all()
    else:
        result = db.query(RegisterCoreMain).order_by(desc(RegisterCoreMain.create_date)).join(RegisterCoreStudent, RegisterCoreMain.rm_id == RegisterCoreStudent.rm_id).filter(
            queryset).options(joinedload(RegisterCoreMain.student_register_core), joinedload(RegisterCoreMain.course_regisetmain_core), joinedload(RegisterCoreMain.branch_regisetmain_core)).offset(skip).limit(limit).all()
    total_data = db.query(RegisterCoreMain).filter(queryset).count()
    total_filter_data = len(result)
    total_page = ceil(total_data / request.per_page)
    return ResponseData(status="success", status_code="200", message="Success fetch all data", page=request.page, per_page=limit, total_page=total_page, total_data=total_data, total_filter_data=total_filter_data, data=result)


@router_register.put("/search_schedule_core/{rm_id}", name="ค้นหาตารางเรียน (แก้ไขข้อมูลหลัก)")
async def search_schedule_core(rm_id: str, request: SearchScheduleInSchema, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _register = db.query(RegisterCoreMain).filter(
        RegisterCoreMain.rm_id == rm_id).one_or_none()
    if not _register:
        raise HTTPException(status_code=404, detail="Data not found")
    date_set = request.date_set
    # ปรับปรุงวันที่ค้นหา
    _register.date_set = date_set
    _register.update_date = todaytime()
    db.commit()
    return {"update": True}


@router_register.get("/get_schedule_core/{rm_id}", name="ปฏิทินการสอนปฏิบัติของครูทั้งหมดอ้างอิงข้อมูลหลัก")
async def get_schedule_core(rm_id: str, teacher_id: str, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):

    _data = db.query(RegisterCoreMain).filter(
        RegisterCoreMain.rm_id == rm_id).one_or_none()
    if not _data:
        raise HTTPException(status_code=404, detail="Data not found")
    obj = []
    year, month, day = datetimeSplit(str(_data.date_set) + " 00:00:00", 2)
    _register = db.query(RegisterCoreSchedule).filter(
        RegisterCoreSchedule.rm_id == rm_id,
        RegisterCoreSchedule.subject_learn_type == 2).all()
    _register_tmp = db.query(RegisterTmpSchedule).filter(
        extract('month', RegisterTmpSchedule.rs_start_time) == month,
        extract('year', RegisterTmpSchedule.rs_start_time) == year,
        RegisterTmpSchedule.teacher_id == teacher_id,
        RegisterTmpSchedule.subject_learn_type == 2,
    ).all()
    _register_main = db.query(RegisterCoreSchedule).filter(
        extract('month', RegisterCoreSchedule.rs_start_time) == month,
        extract('year', RegisterCoreSchedule.rs_start_time) == year,
        RegisterCoreSchedule.rm_id != rm_id,
        RegisterCoreSchedule.teacher_id == teacher_id,
        RegisterCoreSchedule.subject_learn_type == 2,
    ).all()
    if _register:
        for row in _register:
            content = fullcalendarTypeAOutSchema(
                id=row.rs_id,
                title="(" + str(floattoint(row.rs_hour)) + ") " +
                str(row.subject_rcs.subject_name),
                start=row.rs_start_time,
                end=row.rs_end_time,
                editable=True,
                backgroundColor=""
            )
            obj.append(content)
    if _register_tmp:
        for row1 in _register_tmp:

            content1 = fullcalendarTypeAOutSchema(
                title="(" + str(floattoint(row1.rs_hour)) + ") " +
                str(row1.subject_rts.subject_name),
                start=row1.rs_start_time,
                end=row1.rs_end_time,
                editable=False,
                backgroundColor="#f5ab16"
            )

            obj.append(content1)
    if _register_main:
        for row2 in _register_main:
            content2 = fullcalendarTypeAOutSchema(
                title="(" + str(floattoint(row2.rs_hour)) + ") " +
                str(row2.subject_rcs.subject_name),
                start=row2.rs_start_time,
                end=row2.rs_end_time,
                editable=False,
                backgroundColor="#33d406"
            )
            obj.append(content2)
    return obj


@router_register.post("/create_schedule_core", name="บันทึกรายวิชาลงในปฏิทินข้อมูลหลัก")
async def create_schedule_core(request: RegisterScheduleInSchema, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    rm_id = request.rm_id
    subject_learn_type = request.subject_learn_type
    _data = db.query(RegisterCoreMain).filter(
        RegisterCoreMain.rm_id == rm_id).one_or_none()
    if not _data:
        raise HTTPException(status_code=404, detail="Data not found")
    vehicle_type_id = _data.vehicle_type_id
    rs_start_time = request.rs_start_time
    rs_end_time = request.rs_end_time

    teacher_id = request.teacher_id
    # print(rs_start_time)
    # ลบออก 1 วิ เพื่อใช้คำสั่ง between เวลาต่อเนื่องได้
    datestart, timestart = datetimeSplit(rs_start_time, 1)
    dateend, timeend = datetimeSplit(rs_end_time, 1)
    newtimestart = str(datestart) + " " + plusSecond(timestart, 1)
    newtimeend = str(dateend) + " " + minusSecond(timeend, 1)
    hourstart = datetimeSplit(rs_start_time, 3)[0]
    hourend = datetimeSplit(rs_end_time, 3)[0]

    # ปรับปรุงวันที่ค้นหา
    _data.date_set = datestart
    _data.update_date = todaytime()
    db.commit()
    # คำนวนชั่วโมง
    rs_hour = time_difference(
        timestart, timeend)
    # ตรวจสอบว่าตารางเรียนซ้ำกันหรือไม่
    chkteacherTmpSchedule = db.query(RegisterTmpSchedule).filter(
        func.date(RegisterTmpSchedule.rs_start_time) == datestart,
        or_(RegisterTmpSchedule.rs_start_time.between(newtimestart, newtimeend),
            RegisterTmpSchedule.rs_end_time.between(newtimestart, newtimeend),
            and_(extract('hour', RegisterTmpSchedule.rs_start_time) <= int(hourstart),
            extract('hour', RegisterTmpSchedule.rs_end_time) >= int(hourend))
            ),
        RegisterTmpSchedule.teacher_id == teacher_id,
        RegisterTmpSchedule.subject_learn_type == subject_learn_type
    ).count()
    chkteacherMainSchedule = db.query(RegisterCoreSchedule).filter(
        func.date(RegisterCoreSchedule.rs_start_time) == datestart,
        or_(RegisterCoreSchedule.rs_start_time.between(newtimestart, newtimeend),
            RegisterCoreSchedule.rs_end_time.between(newtimestart, newtimeend),
            and_(extract('hour', RegisterCoreSchedule.rs_start_time) <= int(hourstart),
            extract('hour', RegisterCoreSchedule.rs_end_time) >= int(hourend))
            ),
        RegisterCoreSchedule.teacher_id == teacher_id,
        RegisterCoreSchedule.subject_learn_type == subject_learn_type
    ).count()
    # print(chkteacherMainSchedule)
    # ถ้าเป็นรถยนต์ไม่สามารถให้ซ้อนซ้ำกันได้
    if chkteacherTmpSchedule > 0 and vehicle_type_id == 1:
        raise HTTPException(status_code=404, detail="Data not found")
    if chkteacherMainSchedule > 0 and vehicle_type_id == 1:
        raise HTTPException(status_code=404, detail="Data not found")
    # คำนวนชั่วโมงรายวิชาที่บันทึกไปแล้ว
    get_sum_hour = db.query(func.sum(RegisterCoreSchedule.rs_hour).label('sum_hour')).filter(
        RegisterCoreSchedule.subject_id == request.subject_id, RegisterCoreSchedule.rm_id == rm_id,
        RegisterCoreSchedule.subject_learn_type == subject_learn_type).first()
    sum_hour = noneToZero(get_sum_hour.sum_hour) + float(rs_hour)
    _subject = db.query(RegisterCoreCachSubject).filter(
        RegisterCoreCachSubject.subject_id == request.subject_id, RegisterCoreCachSubject.rm_id == rm_id).one_or_none()
    if _subject:
        # ถ้าชั่วโมงที่บันทึกมากกว่า โควดต้าชั่วโมงที่กำหนด
        if sum_hour > _subject.rs_hour_quota:
            raise HTTPException(status_code=404, detail="Data not found")

        calHour = float(_subject.rs_hour_quota) - \
            float(sum_hour)
        _subject.rs_hour_use = calHour
        db.commit()

    _register = RegisterCoreSchedule(
        subject_learn_type=request.subject_learn_type,
        rs_start_time=rs_start_time,
        rs_end_time=rs_end_time,
        rs_hour=rs_hour,
        create_date=todaytime(),
        update_date=todaytime(),
        subject_id=request.subject_id,
        teacher_id=teacher_id,
        rm_id=rm_id,
        branch_id=request.branch_id,
        school_id=request.school_id
    )
    db.add(_register)
    db.commit()

    return ResponseProcess(status="success", status_code="200",  message="Success Create data")


@router_register.put("/update_schedule_core/{rs_id}", name="แก้ไขตารางเรียนของข้อมูลหลัก")
async def update_schedule_core(rs_id: str, request: RegisterScheduleInUpdateSchema, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _register = db.query(RegisterCoreSchedule).filter(
        RegisterCoreSchedule.rs_id == rs_id).one_or_none()
    if not _register:
        raise HTTPException(status_code=404, detail="Data not found")

    rm_id = _register.rm_id
    _data = db.query(RegisterCoreMain).filter(
        RegisterCoreMain.rm_id == rm_id).one_or_none()
    vehicle_type_id = _data.vehicle_type_id
    rs_start_time = request.rs_start_time
    rs_end_time = request.rs_end_time
    teacher_id = _register.teacher_id
    subject_learn_type = _register.subject_learn_type
    # ลบออก 1 วิ เพื่อใช้คำสั่ง between เวลาต่อเนื่องได้
    datestart, timestart = datetimeSplit(rs_start_time, 1)
    dateend, timeend = datetimeSplit(rs_end_time, 1)
    newtimestart = str(datestart) + " " + plusSecond(timestart, 1)
    newtimeend = str(dateend) + " " + minusSecond(timeend, 1)

    hourstart = datetimeSplit(rs_start_time, 3)[0]
    hourend = datetimeSplit(rs_end_time, 3)[0]
    # print(hourstart)
    # ตรวจสอบว่าตารางเรียนซ้ำกันหรือไม่
    chkteacherTmpSchedule = db.query(RegisterTmpSchedule).filter(
        func.date(RegisterTmpSchedule.rs_start_time) == datestart,
        or_(RegisterTmpSchedule.rs_start_time.between(newtimestart, newtimeend),
            RegisterTmpSchedule.rs_end_time.between(newtimestart, newtimeend),
            and_(extract('hour', RegisterTmpSchedule.rs_start_time) <= int(hourstart),
            extract('hour', RegisterTmpSchedule.rs_end_time) >= int(hourend))
            ),
        RegisterTmpSchedule.teacher_id == teacher_id,
        RegisterTmpSchedule.subject_learn_type == subject_learn_type

    ).count()
    chkteacherMainSchedule = db.query(RegisterCoreSchedule).filter(
        func.date(RegisterCoreSchedule.rs_start_time) == datestart,
        or_(RegisterCoreSchedule.rs_start_time.between(newtimestart, newtimeend),
            RegisterCoreSchedule.rs_end_time.between(newtimestart, newtimeend),
            and_(extract('hour', RegisterCoreSchedule.rs_start_time) <= int(hourstart),
            extract('hour', RegisterCoreSchedule.rs_end_time) >= int(hourend))
            ),
        RegisterCoreSchedule.rs_id != rs_id,
        RegisterCoreSchedule.teacher_id == teacher_id,
        RegisterCoreSchedule.subject_learn_type == subject_learn_type
    ).count()

    # ถ้าเป็นรถยนต์ไม่สามารถให้ซ้อนซ้ำกันได้
    if chkteacherTmpSchedule > 0 and vehicle_type_id == 1:
        raise HTTPException(status_code=404, detail="Data not found")
    if chkteacherMainSchedule > 0 and vehicle_type_id == 1:
        raise HTTPException(status_code=404, detail="Data not found")

    subject_id = _register.subject_id

   # คำนวนชั่วโมง
    rs_hour = time_difference(
        timestart, timeend)

    # คำนวนชั่วโมงรายวิชาที่บันทึกไปแล้ว
    get_sum_hour = db.query(func.sum(RegisterCoreSchedule.rs_hour).label('sum_hour')).filter(
        RegisterCoreSchedule.rs_id != rs_id, RegisterCoreSchedule.subject_id == subject_id, RegisterCoreSchedule.rm_id == rm_id,
        RegisterCoreSchedule.subject_learn_type == subject_learn_type).first()
    sum_hour = noneToZero(get_sum_hour.sum_hour) + float(rs_hour)

    _subject = db.query(RegisterCoreCachSubject).filter(
        RegisterCoreCachSubject.subject_id == subject_id, RegisterCoreCachSubject.rm_id == rm_id).one_or_none()

    if _subject:
        # ถ้าชั่วโมงที่บันทึกมากกว่า โควต้าชั่วโมงที่กำหนด
        if sum_hour > _subject.rs_hour_quota:
            raise HTTPException(status_code=404, detail="Data not found")
        calHour = float(_subject.rs_hour_quota) - \
            float(sum_hour)
        _subject.rs_hour_use = calHour
        db.commit()

    _register.rs_start_time = rs_start_time
    _register.rs_end_time = rs_end_time
    _register.rs_hour = rs_hour
    db.commit()

    # debug = str(sum_hour) + " " + str(_subject.rs_hour_quota)

    return ResponseProcess(status="success", status_code="200", message="Success Update data")


@router_register.delete("/subject_schedule_core/{rs_id}", name="ลบรายวิชาข้อมูลหลักจากปฏิทินการสอน")
async def delete_schedule_core(rs_id: str, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _register = db.query(RegisterCoreSchedule).filter(
        RegisterCoreSchedule.rs_id == rs_id).one_or_none()
    if not _register:
        raise HTTPException(status_code=404, detail="Data not found")
    rs_hour = _register.rs_hour
    subject_id = _register.subject_id
    rm_id = _register.rm_id
    db.delete(_register)
    db.commit()
    # คืนเวลาที่พึ่งลบไป
    _subject = db.query(RegisterCoreCachSubject).filter(
        RegisterCoreCachSubject.subject_id == subject_id, RegisterCoreCachSubject.rm_id == rm_id).one_or_none()
    calHour = float(_subject.rs_hour_use) + float(rs_hour)
    _subject.rs_hour_use = calHour
    db.commit()
    return ResponseProcess(status="success", status_code="200", message="Success delete data")


@router_register.get("/schedule_detail_core/{rs_id}")
def schedule_detail_core(rs_id: str,  db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _register = db.query(RegisterCoreSchedule).filter(
        RegisterCoreSchedule.rs_id == rs_id).options(joinedload(RegisterCoreSchedule.teacher_rcs)).one_or_none()
    if not _register:
        raise HTTPException(status_code=404, detail="Data not found")
    return _register


@router_register.post("/student_core", name="บันทึกข้อมูลนักเรียนข้อมูลหลัก")
async def update_student_core(request: RegisterStudentInSchema, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    rm_id = request.rm_id
    _student = db.query(RegisterCoreStudent).filter(
        RegisterCoreStudent.rm_id == rm_id).one_or_none()
    if not _student:
        raise HTTPException(status_code=404, detail="Data not found")
    _student.student_cover = request.student_cover
    _student.student_prefix = request.student_prefix,
    _student.student_firstname = request.student_firstname
    _student.student_lastname = request.student_lastname
    _student.student_id_number = request.student_id_number
    _student.student_birthday = request.student_birthday
    _student.student_gender = request.student_gender,
    _student.student_mobile = request.student_mobile
    _student.student_email = request.student_email
    _student.student_address = request.student_address
    _student.update_date = todaytime(),
    _student.location_id = request.location_id
    _student.country_id = request.country_id
    _student.nationality_id = request.nationality_id
    _student.branch_id = request.branch_id
    _student.school_id = request.school_id
    db.commit()
    return ResponseProcess(status="success", status_code="200", message="Success update data")


@router_register.post("/create_schedule_core_multiple", name="บันทึกรายวิชาลงในปฏิทินข้อมูลหลักแบบหลายวิชาพร้อมกัน")
async def create_schedule_core_multiple(request: list[RegisterScheduleInSchema], db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    rm_id = request[0].rm_id
    subject_learn_type = request[0].subject_learn_type
    _data = db.query(RegisterCoreMain).filter(
        RegisterCoreMain.rm_id == rm_id).one_or_none()
    if not _data:
        raise HTTPException(status_code=404, detail="Data not found")
    db.query(RegisterCoreSchedule).filter(
        RegisterCoreSchedule.subject_learn_type == subject_learn_type, RegisterCoreSchedule.rm_id == rm_id).delete()
    db.commit()
    obj = []
    for row in request:
        timestart = datetimeSplit(row.rs_start_time, 1)[1]
        timeend = datetimeSplit(row.rs_end_time, 1)[1]
        rs_hour = time_difference(
            timestart, timeend)
        _register = RegisterCoreSchedule(
            subject_learn_type=subject_learn_type,
            rs_start_time=row.rs_start_time,
            rs_end_time=row.rs_end_time,
            rs_hour=rs_hour,
            create_date=todaytime(),
            update_date=todaytime(),
            subject_id=row.subject_id,
            teacher_id=row.teacher_id,
            rm_id=rm_id,
            branch_id=row.branch_id,
            school_id=row.school_id
        )
        obj.append(_register)
    db.add_all(obj)
    db.commit()
    return ResponseProcess(status="success", status_code="200",  message="Success Create data")


@router_register.get("/update_exam_core/{rm_id}/{ed_id}", name="แก้ไขวันสอบจากข้อมูลหลัก")
async def update_exam_core(rm_id: str, ed_id: int, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):

    _register = db.query(RegisterCoreMain).filter(
        RegisterCoreMain.rm_id == rm_id).one_or_none()
    if not _register:
        raise HTTPException(status_code=404, detail="Data not found")
    _register.ed_id = ed_id
    db.commit()
    return ResponseProcess(status="success", status_code="200", message="Success update data")


@router_register.post("/report/list/learn/{school_id}", name="รายงานจบหลักสูตรและไม่จบหลักสูตร")
async def list_learn_success(request: FilterRequestSchema, school_id: str, rm_success: bool, month: int, year: int, branch_id: str = "all",   db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    skip = ternaryZero(((request.page - 1) * request.per_page))
    limit = request.per_page
    search_value = request.search_value
    if branch_id != 'all':
        # โชว์ครูเฉพาะสาขาตนเอง
        queryset = RegisterCoreMain.branch_id == branch_id
    else:
        queryset = RegisterCoreMain.school_id == school_id
    searchFilter = or_(RegisterCoreStudent.student_firstname.contains(search_value),
                       RegisterCoreStudent.student_lastname.contains(
                           search_value),
                       RegisterCoreStudent.student_id_number.contains(
                           search_value),
                       RegisterCoreStudent.student_mobile.contains(
                           search_value),
                       RegisterCoreMain.rm_doc_number.contains(search_value))

    if search_value:
        result = db.query(RegisterCoreMain).order_by(desc(RegisterCoreMain.create_date)).join(RegisterCoreStudent, RegisterCoreMain.rm_id == RegisterCoreStudent.rm_id).filter(
            queryset, searchFilter, RegisterCoreMain.rm_success == rm_success, extract('year', RegisterCoreMain.create_date) == year, extract('month', RegisterCoreMain.create_date) == month).options(joinedload(RegisterCoreMain.student_register_core), joinedload(RegisterCoreMain.branch_regisetmain_core)).offset(skip).limit(limit).all()
    else:
        result = db.query(RegisterCoreMain).order_by(desc(RegisterCoreMain.create_date)).join(RegisterCoreStudent, RegisterCoreMain.rm_id == RegisterCoreStudent.rm_id).filter(
            queryset, RegisterCoreMain.rm_success == rm_success, extract('year', RegisterCoreMain.create_date) == year, extract('month', RegisterCoreMain.create_date) == month).options(joinedload(RegisterCoreMain.student_register_core), joinedload(RegisterCoreMain.branch_regisetmain_core)).offset(skip).limit(limit).all()
    total_data = db.query(RegisterCoreMain).filter(
        queryset, RegisterCoreMain.rm_success == rm_success, extract('year', RegisterCoreMain.create_date) == year, extract('month', RegisterCoreMain.create_date) == month).count()
    total_filter_data = len(result)
    total_page = ceil(total_data / request.per_page)
    return ResponseData(status="success", status_code="200", message="Success fetch all data", page=request.page, per_page=limit, total_page=total_page, total_data=total_data, total_filter_data=total_filter_data, data=result)


@router_register.post("/report/pay/partial/{school_id}", name="รายงานยอดค้างชำระ")
async def list_pay_partial(request: FilterRequestSchema, school_id: str, month: int, year: int, branch_id: str = "all", db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    skip = ternaryZero(((request.page - 1) * request.per_page))
    limit = request.per_page
    search_value = request.search_value
    if branch_id != 'all':
        # โชว์ครูเฉพาะสาขาตนเอง
        queryset = RegisterCoreMain.branch_id == branch_id
    else:
        queryset = RegisterCoreMain.school_id == school_id
    searchFilter = or_(RegisterCoreStudent.student_firstname.contains(search_value),
                       RegisterCoreStudent.student_lastname.contains(
                           search_value),
                       RegisterCoreStudent.student_id_number.contains(
                           search_value),
                       RegisterCoreStudent.student_mobile.contains(
                           search_value),
                       RegisterCoreMain.rm_doc_number.contains(search_value)
                       )

    if search_value:
        result = db.query(RegisterCoreMain).order_by(desc(RegisterCoreMain.create_date)).join(RegisterCoreStudent, RegisterCoreMain.rm_id == RegisterCoreStudent.rm_id).filter(
            queryset, searchFilter, RegisterCoreMain.rm_pay_status == "PP", extract('year', RegisterCoreMain.create_date) == year, extract('month', RegisterCoreMain.create_date) == month).options(joinedload(RegisterCoreMain.student_register_core), joinedload(RegisterCoreMain.branch_regisetmain_core), joinedload(RegisterCoreMain.payment_rcm)).offset(skip).limit(limit).all()
    else:
        result = db.query(RegisterCoreMain).order_by(desc(RegisterCoreMain.create_date)).join(RegisterCoreStudent, RegisterCoreMain.rm_id == RegisterCoreStudent.rm_id).filter(
            queryset, RegisterCoreMain.rm_pay_status == "PP", extract('year', RegisterCoreMain.create_date) == year, extract('month', RegisterCoreMain.create_date) == month).options(joinedload(RegisterCoreMain.student_register_core), joinedload(RegisterCoreMain.branch_regisetmain_core),  joinedload(RegisterCoreMain.payment_rcm)).offset(skip).limit(limit).all()
    total_data = db.query(RegisterCoreMain).filter(
        queryset, RegisterCoreMain.rm_pay_status == "PP", extract('year', RegisterCoreMain.create_date) == year, extract('month', RegisterCoreMain.create_date) == month).count()
    total_filter_data = len(result)
    total_page = ceil(total_data / request.per_page)

    return ResponseData(status="success", status_code="200", message="Success fetch all data", page=request.page, per_page=limit, total_page=total_page, total_data=total_data, total_filter_data=total_filter_data, data=result)
