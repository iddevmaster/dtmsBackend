from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import asc, desc, extract, or_
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import func

from authen import auth_request
from data_common import base_school_id
from database import get_db
from function import (ceil, noneToZero, subject_learn_typeConvert, ternaryZero,
                      time_difference, todaytime, rows_limit)
from models import (Course, CoursePrice, CourseWithSubject, ExamDate,
                    ExamDateDirector, Seminar, Subject)
from schemas_format.general_schemas import (
    FilterRequestSchema, ResponseProcess, ResponseData)
from schemas_format.course_schemas import (CoursePriceRequestInSchema, CourseRequestInSchema, CourseRequestOutSchema, ExamDateDirectorRequestInSchema, ExamDateRequestInSchema, SeminarRequestInSchema,
                                           SeminarRequestOutSchema, ExamDateRequestOutSchema, ExamDateDirectorRequestOutSchema, SeminarRequestMutipleInSchema,
                                           SubjectRequestInSchema, SubjectCourseRequestInSchema, SubjectRequestOutSchema, SubjectCourseRequestOutSchema)

router_course = APIRouter()


@router_course.post("/subject/create")
def create_subject(request: SubjectRequestInSchema, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    if request.subject_type != 1 and request.subject_type != 2:
        raise HTTPException(status_code=404, detail="Data not found")

    if request.subject_learn_type != 1 and request.subject_learn_type != 2:
        raise HTTPException(status_code=404, detail="Data not found")

    _subject = Subject(
        subject_code=request.subject_code,
        subject_name=request.subject_name,
        subject_type=request.subject_type,
        subject_learn_type=request.subject_learn_type,
        create_date=todaytime(),
        update_date=todaytime(),
        vehicle_type_id=request.vehicle_type_id,
        school_id=request.school_id
    )
    db.add(_subject)
    db.commit()
    db.refresh(_subject)
    return ResponseProcess(status="success", status_code="200", message="Success created data")


@router_course.post("/subject/{school_id}")
def get_subject(school_id: str, only: bool, request: FilterRequestSchema, db: Session = Depends(get_db),  authenticated: bool = Depends(auth_request)):
    skip = ternaryZero(((request.page - 1) * request.per_page))
    limit = rows_limit(request.per_page)
    search_value = request.search_value
    result = db.query(Subject).order_by(
        desc(Subject.create_date)).filter(Subject.cancelled == 1)
    total_data = result.count()
    if only == True:
        # โชว์หลักสูตรกลางและของตนเอง
        result = result.filter(
            or_(Subject.school_id == school_id, Subject.school_id == base_school_id))
    else:
        result = result.filter(Subject.school_id == school_id)
    if search_value:
        result = result.filter(or_(Subject.subject_code.contains(
            search_value), Subject.subject_name.contains(search_value)))
    total_filter_data = result.count()
    result = result.offset(skip).limit(limit).all()
    total_page = ceil(total_data / request.per_page)
    content = [SubjectRequestOutSchema.from_orm(p) for p in result]
    return ResponseData(status="success", status_code="200", message="Success fetch all data", page=request.page, per_page=limit, total_page=total_page, total_data=total_data, total_filter_data=total_filter_data, data=content)


@router_course.get("/subject/{subject_learn_type}/{vehicle_type_id}/{school_id}", response_model=list[SubjectRequestOutSchema])
def get_subject_filter(subject_learn_type: int, vehicle_type_id: int, school_id: str,  db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _subject = db.query(Subject).options(joinedload(Subject.school_subject)).order_by(desc(Subject.create_date)).filter(
        Subject.subject_learn_type == subject_learn_type, Subject.vehicle_type_id == vehicle_type_id, Subject.active == 1, Subject.school_id == school_id).all()
    if not _subject:
        raise HTTPException(status_code=404, detail="Data not found")
    return _subject


@router_course.get("/subject/{subject_id}", response_model=SubjectRequestOutSchema)
def get_by_subject_id(subject_id: int,  db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _subject = db.query(Subject).options(joinedload(Subject.school_subject)).filter(
        Subject.subject_id == subject_id).one_or_none()
    if not _subject:
        raise HTTPException(status_code=404, detail="Data not found")
    return _subject


@router_course.put("/subject/{subject_id}")
def update_subject(subject_id: int, request: SubjectRequestInSchema,  db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _subject = db.query(Subject).filter(
        Subject.subject_id == subject_id).one_or_none()
    if not _subject:
        raise HTTPException(status_code=404, detail="Data not found")

    _subject.subject_code = request.subject_code
    _subject.subject_name = request.subject_name
    _subject.subject_type = request.subject_type
    _subject.subject_learn_type = request.subject_learn_type
    _subject.active = request.active
    _subject.vehicle_type_id = request.vehicle_type_id
    _subject.school_id = request.school_id

    db.commit()
    db.refresh(_subject)
    return ResponseProcess(status="success", status_code="200", message="Success update data")


@router_course.delete("/subject/{subject_id}")
def delete_subject(subject_id: int, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _subject = db.query(Subject).filter(
        Subject.subject_id == subject_id).one_or_none()
    if not _subject:
        raise HTTPException(status_code=404, detail="Data not found")
    # db.delete(_subject)
    _subject.cancelled = 0
    db.commit()
    return ResponseProcess(status="success", status_code="200", message="Success delete data")


@router_course.post("/create")
def create_course(request: CourseRequestInSchema, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):

    _course = Course(
        course_code=request.course_code,
        course_name=request.course_name,
        course_theory_hour=request.course_theory_hour,
        course_practice_hour=request.course_practice_hour,
        course_total_hour=request.course_total_hour,
        course_readey=request.course_readey,
        course_group=request.course_group,
        create_date=todaytime(),
        update_date=todaytime(),
        vehicle_type_id=request.vehicle_type_id,
        school_id=request.school_id
    )
    db.add(_course)
    db.commit()
    db.refresh(_course)
    return ResponseProcess(status="success", status_code="200", message="Success created data ")


@router_course.post("/{school_id}")
def get_course(school_id: str, only: bool, request: FilterRequestSchema, db: Session = Depends(get_db),  authenticated: bool = Depends(auth_request)):
    skip = ternaryZero(((request.page - 1) * request.per_page))
    limit = rows_limit(request.per_page)
    search_value = request.search_value
    result = db.query(Course).order_by(
        desc(Course.create_date)).filter(Course.cancelled == 1)
    if only == True:
        # โชว์หลักสูตรกลางและของตนเอง
        result = result.filter(
            or_(Course.school_id == school_id, Course.school_id == base_school_id))
    else:
        result = result.filter(Course.school_id == school_id)
    total_data = result.count()
    if search_value:
        result = result.filter(or_(Course.course_code.contains(
            search_value), Course.course_name.contains(search_value)))
    total_filter_data = result.count()
    result = result.offset(skip).limit(limit).all()
    total_page = ceil(total_data / request.per_page)
    content = [CourseRequestOutSchema.from_orm(p) for p in result]
    return ResponseData(status="success", status_code="200", message="Success fetch all data", page=request.page, per_page=limit, total_page=total_page, total_data=total_data, total_filter_data=total_filter_data, data=content)


@router_course.put("/{course_id}")
def update_course(course_id: str, request: CourseRequestInSchema,  db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _course = db.query(Course).filter(
        Course.course_id == course_id).one_or_none()
    if not _course:
        raise HTTPException(status_code=404, detail="Data not found")
    _course.course_code = request.course_code
    _course.course_name = request.course_name
    _course.course_theory_hour = request.course_theory_hour
    _course.course_practice_hour = request.course_practice_hour
    _course.course_total_hour = request.course_total_hour
    _course.course_readey = request.course_readey
    _course.course_group = request.course_group
    _course.active = request.active
    _course.vehicle_type_id = request.vehicle_type_id
    _course.school_id = request.school_id

    db.commit()
    db.refresh(_course)
    return ResponseProcess(status="success", status_code="200", message="Success update data")


@router_course.get("/{course_id}", response_model=CourseRequestOutSchema)
def get_by_course_id(course_id: str,  db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _course = db.query(Course).options(joinedload(Course.school_course)).filter(
        Course.course_id == course_id).one_or_none()
    if not _course:
        raise HTTPException(status_code=404, detail="Data not found")
    return _course


@router_course.delete("/{course_id}")
def delete_course(course_id: str, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _course = db.query(Course).filter(
        Course.course_id == course_id).one_or_none()
    if not _course:
        raise HTTPException(status_code=404, detail="Data not found")
    _course.cancelled = 0
    db.commit()
    return ResponseProcess(status="success", status_code="200", message="Success delete data")


@router_course.post("/c/price")
def create_course_price(request: CoursePriceRequestInSchema, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _course = db.query(CoursePrice).filter(
        CoursePrice.course_id == request.course_id, CoursePrice.branch_id == request.branch_id).one_or_none()
    if not _course:
        course = CoursePrice(
            cp_price=request.cp_price,
            course_id=request.course_id,
            branch_id=request.branch_id,
            school_id=request.school_id,
        )
        db.add(course)
    else:
        _course.cp_price = request.cp_price
    db.commit()
    return ResponseProcess(status="success", status_code="200", message="Success created data")


@router_course.get("/c/price/{course_id}/{school_id}")
def get_course_price(course_id: str, school_id: str, branch_id: str = "all", db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    if branch_id == "all":
        _course = db.query(CoursePrice).filter(
            CoursePrice.course_id == course_id, CoursePrice.school_id == school_id).options(joinedload(CoursePrice.branch_course_price)).all()
    else:
        _course = db.query(CoursePrice).filter(
            CoursePrice.course_id == course_id, CoursePrice.school_id == school_id, CoursePrice.branch_id == branch_id).options(joinedload(CoursePrice.branch_course_price)).one_or_none()
    return _course


@router_course.delete("/c/price/{cp_id}")
def delete_course_price(cp_id: int, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _course = db.query(CoursePrice).filter(
        CoursePrice.cp_id == cp_id).one_or_none()
    if not _course:
        raise HTTPException(status_code=404, detail="Data not found")
    db.delete(_course)
    db.commit()
    return ResponseProcess(status="success", status_code="200", message="Success delete data")


@router_course.post("/s/add_subject")
def add_subject_course(request: SubjectCourseRequestInSchema, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    course_id = request.course_id
    subject_learn_type = request.subject_learn_type
    learn_time = request.learn_time
    subject_id = request.subject_id
    _course = db.query(CourseWithSubject).filter(
        CourseWithSubject.course_id == course_id, CourseWithSubject.subject_id == request.subject_id).one_or_none()
    # คำนวนชั่วโมงหาผลรวมโดยแยก subject_learn_type และไม่คำนวณรายวิชาที่ส่งมาจากฟอร์ม
    get_sum_hour = db.query(func.sum(CourseWithSubject.learn_time).label('sum_hour')).filter(
        CourseWithSubject.course_id == course_id, CourseWithSubject.subject_learn_type == subject_learn_type, CourseWithSubject.subject_id != subject_id).first()
    # {"sum_hour": 6.0}

    sum_hour = noneToZero(get_sum_hour.sum_hour)
    getCourseData = db.query(Course).filter(
        Course.course_id == course_id).one()
    if subject_learn_type == 1:
        getHourCourse = getCourseData.course_theory_hour
    else:
        getHourCourse = getCourseData.course_practice_hour
    if (float(sum_hour) + float(learn_time)) > float(getHourCourse):
        raise HTTPException(status_code=404, detail="Data not found")

    if not _course:
        course = CourseWithSubject(
            learn_time=learn_time,
            subject_learn_type=subject_learn_type,
            subject_id=subject_id,
            course_id=course_id
        )
        db.add(course)
    else:
        _course.learn_time = request.learn_time
        # ถ้าจำนวนรายวิชามีค่าเท่ากับ 0 ให้ลบทิ้ง
    if learn_time == 0:
        db.delete(_course)

    db.commit()

    get_sum_hour_total = db.query(func.sum(CourseWithSubject.learn_time).label('sum_hour_total')).filter(
        CourseWithSubject.course_id == course_id, CourseWithSubject.subject_learn_type == subject_learn_type).first()

    return {'sum_hour': sum_hour, 'sum_hour_total': get_sum_hour_total.sum_hour_total, 'get_hour_course': getHourCourse, 'join_subject_learn_type': subject_learn_typeConvert(subject_learn_type)}


@router_course.delete("/s/{course_id}")
def empty_subject_course(course_id: str, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _course = db.query(CourseWithSubject).filter(
        CourseWithSubject.course_id == course_id).all()
    if not _course:
        raise HTTPException(status_code=404, detail="Data not found")
    # db.delete(_course)
    # Delete multiple records
    db.query(CourseWithSubject).filter(
        CourseWithSubject.course_id == course_id).delete()
    # Set ให้หลักสูตรอยู่ในสถานะไม่พร้อม
    _course2 = db.query(Course).filter(
        Course.course_id == course_id).one_or_none()
    _course2.course_readey = 0
    db.commit()
    return ResponseProcess(status="success", status_code="200", message="Success delete data")


@router_course.get("/s/{course_id}")
def set_course_ready(course_id: str, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _course = db.query(Course).filter(
        Course.course_id == course_id).one_or_none()
    if not _course:
        raise HTTPException(status_code=404, detail="Data not found")

    # //หาผลรวมชั่วโมงวิชาหมวดทฤษฎี
    get_sum_hour_theory = db.query(func.sum(CourseWithSubject.learn_time).label('sum_hour_total')).filter(
        CourseWithSubject.course_id == course_id, CourseWithSubject.subject_learn_type == 1).first()
    # //หาผลรวมชั่วโมงวิชาหมวดปฏิบัติ
    get_sum_hour_practice = db.query(func.sum(CourseWithSubject.learn_time).label('sum_hour_total')).filter(
        CourseWithSubject.course_id == course_id, CourseWithSubject.subject_learn_type == 2).first()
    if noneToZero(get_sum_hour_theory.sum_hour_total) != _course.course_theory_hour:
        raise HTTPException(status_code=404, detail="Data not found")
    if noneToZero(get_sum_hour_practice.sum_hour_total) != _course.course_practice_hour:
        raise HTTPException(status_code=404, detail="Data not found")
    _course.course_readey = 1
    db.commit()
    return ResponseProcess(status="success", status_code="200", message="Success update data")


@router_course.get("/s/list/{course_id}", response_model=list[SubjectCourseRequestOutSchema])
def get_subject_course(course_id: str, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _subject = db.query(CourseWithSubject).options(joinedload(CourseWithSubject.course_coursewithsubject), joinedload(CourseWithSubject.subject_coursewithsubject)).order_by(asc(CourseWithSubject.subject_learn_type)).filter(
        CourseWithSubject.course_id == course_id).all()
    if not _subject:
        raise HTTPException(status_code=404, detail="Data not found")
    return _subject


@router_course.post("/seminar/create")
def create_seminar(request: SeminarRequestInSchema, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    seminar_hour = time_difference(
        request.seminar_start_time, request.seminar_end_time)
    _seminar = Seminar(
        seminar_start_time=request.seminar_start_time,
        seminar_end_time=request.seminar_end_time,
        seminar_hour=seminar_hour,
        seminar_date=request.seminar_date,
        seminar_ready=request.seminar_ready,
        active=request.active,
        create_date=todaytime(),
        update_date=todaytime(),
        course_id=request.course_id,
        subject_id=request.subject_id,
        teacher_id=request.teacher_id,
        branch_id=request.branch_id,
        school_id=request.school_id
    )
    db.add(_seminar)
    db.commit()
    db.refresh(_seminar)
    return ResponseProcess(status="success", status_code="200", message="Success created data")


@router_course.post("/seminar/create_multiple")
def create_seminar_multiple(request: list[SeminarRequestMutipleInSchema], db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    obj = []
    for row in request:
        seminar_hour = time_difference(
            row.seminar_start_time, row.seminar_end_time)
        # print(len(row.seminar_date_Obj))
        for d in row.seminar_date_Obj:
            seminar_date = d
            _seminar = Seminar(
                seminar_hour=seminar_hour,
                seminar_start_time=row.seminar_start_time,
                seminar_end_time=row.seminar_end_time,
                seminar_date=seminar_date,
                seminar_ready=0,
                create_date=todaytime(),
                update_date=todaytime(),
                subject_id=row.subject_id,
                course_id=row.course_id,
                teacher_id=row.teacher_id,
                branch_id=row.branch_id,
                school_id=row.school_id
            )
            obj.append(_seminar)
            # db.add(_seminar)
            # db.commit()
    db.add_all(obj)
    db.commit()
    return ResponseProcess(status="success", status_code="200", message="Success created data")


@router_course.put("/seminar/{seminar_id}")
def update_seminar(seminar_id: int, request: SeminarRequestInSchema, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _seminar = db.query(Seminar).filter(
        Seminar.seminar_id == seminar_id).one_or_none()
    if not _seminar:
        raise HTTPException(status_code=404, detail="Data not found")
    seminar_hour = time_difference(
        request.seminar_start_time, request.seminar_end_time)
    _seminar.seminar_start_time = request.seminar_start_time
    _seminar.seminar_end_time = request.seminar_end_time
    _seminar.seminar_hour = seminar_hour
    _seminar.seminar_date = request.seminar_date
    _seminar.seminar_ready = request.seminar_ready
    _seminar.active = request.active
    _seminar.update_date = todaytime()
    _seminar.subject_id = request.subject_id,
    _seminar.course_id = request.course_id
    _seminar.teacher_id = request.teacher_id
    _seminar.branch_id = request.branch_id
    _seminar.school_id = request.school_id
    db.commit()
    return ResponseProcess(status="success", status_code="200", message="Success update data")


@router_course.get("/seminar/{seminar_id}", response_model=SeminarRequestOutSchema)
def get_by_seminar_id(seminar_id: int,  db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _seminar = db.query(Seminar).options(joinedload(Seminar.subject_seminar),
                                         joinedload(Seminar.course_seminar),
                                         joinedload(Seminar.teacher_seminar),
                                         joinedload(Seminar.branch_seminar),
                                         joinedload(Seminar.school_seminar)).filter(Seminar.seminar_id == seminar_id).one_or_none()
    if not _seminar:
        raise HTTPException(status_code=404, detail="Data not found")
    return _seminar


@router_course.get("/seminar/{school_id}/{course_id}", response_model=list[SeminarRequestOutSchema])
def get_seminar(school_id: str, course_id: str,   month: int, year: int, branch_id: str = "all",   db: Session = Depends(get_db),  authenticated: bool = Depends(auth_request)):
    _subject = db.query(Seminar).options(joinedload(Seminar.subject_seminar),
                                         joinedload(Seminar.course_seminar),
                                         joinedload(Seminar.teacher_seminar),
                                         joinedload(Seminar.branch_seminar),
                                         joinedload(Seminar.school_seminar)).order_by(asc(Seminar.seminar_date)).filter(
        Seminar.cancelled == 1, Seminar.course_id == course_id,  extract('year', Seminar.seminar_date) == year, extract('month', Seminar.seminar_date) == month)
    if branch_id != 'all':
        # โชว์วิชาอบรมเฉพาะสาขาตนเอง
        _subject = _subject.filter(Seminar.branch_id == branch_id)
    else:
        _subject = _subject.filter(Seminar.school_id == school_id)
    _subject = _subject.all()
    return _subject


@router_course.delete("/seminar/{seminar_id}")
def delete_seminar(seminar_id: int, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _seminar = db.query(Seminar).filter(
        Seminar.seminar_id == seminar_id).one_or_none()
    if not _seminar:
        raise HTTPException(status_code=404, detail="Data not found")
    _seminar.cancelled = 0
    # db.delete(_seminar)
    db.commit()
    return ResponseProcess(status="success", status_code="200", message="Success delete data")


@router_course.post("/examdate/create")
def create_examdate(request: ExamDateRequestInSchema, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    # ตรวจสอบว่าเคยมีการเพิ่มครูในระบบหรือไม่
    chkteacher = db.query(ExamDateDirector).filter(
        ExamDateDirector.ed_code == request.ed_code).one_or_none()
    if not chkteacher:
        raise HTTPException(status_code=404, detail="Data not found")
    ed_hour = time_difference(
        request.ed_start_time, request.ed_end_time)
    _examdate = ExamDate(
        ed_start_time=request.ed_start_time,
        ed_end_time=request.ed_end_time,
        ed_hour=ed_hour,
        ed_date=request.ed_date,
        ed_ready=request.ed_ready,
        ed_code=request.ed_code,
        active=request.active,
        create_date=todaytime(),
        update_date=todaytime(),
        vehicle_type_id=request.vehicle_type_id,
        branch_id=request.branch_id,
        school_id=request.school_id
    )
    db.add(_examdate)
    db.commit()
    db.refresh(_examdate)
    return ResponseProcess(status="success", status_code="200", message="Success created data")


@router_course.post("/examdate/director/create")
def create_examdate_director(request: ExamDateDirectorRequestInSchema, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    # ตรวจสอบว่าเคยมีการเพิ่มครูท่านนี้ในระบบหรือไม่
    chkteacher = db.query(ExamDateDirector).filter(
        ExamDateDirector.teacher_id == request.teacher_id, ExamDateDirector.ed_code == request.ed_code).one_or_none()
    if chkteacher:
        raise HTTPException(status_code=404, detail="Data not found")

    _examdate = ExamDateDirector(
        ed_code=request.ed_code,
        staff_exam_type=request.staff_exam_type,
        teacher_id=request.teacher_id
    )
    db.add(_examdate)
    db.commit()
    db.refresh(_examdate)
    return ResponseProcess(status="success", status_code="200", message="Success created data")


@router_course.get("/examdate/director/{ed_code}", response_model=list[ExamDateDirectorRequestOutSchema])
def get_examdate_director(ed_code: str, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _examdate = db.query(ExamDateDirector).options(joinedload(ExamDateDirector.teacher_examdate_dt)).order_by(asc(ExamDateDirector.edd_id)).filter(
        ExamDateDirector.ed_code == ed_code).all()
    return _examdate


@router_course.delete("/examdate/director/{edd_id}")
def delete_examdate_director(edd_id: int, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _examdate = db.query(ExamDateDirector).filter(
        ExamDateDirector.edd_id == edd_id).one_or_none()
    if not _examdate:
        raise HTTPException(status_code=404, detail="Data not found")
    db.delete(_examdate)
    db.commit()
    return ResponseProcess(status="success", status_code="200", message="Success delete data")


@router_course.put("/examdate/{ed_id}")
def update_examdate(ed_id: int, request: ExamDateRequestInSchema, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    # ตรวจสอบว่าเคยมีการเพิ่มครูในระบบหรือไม่
    chkteacher = db.query(ExamDateDirector).filter(
        ExamDateDirector.ed_code == request.ed_code).one_or_none()
    if not chkteacher:
        raise HTTPException(status_code=404, detail="Data not found")
    _examdate = db.query(ExamDate).filter(
        ExamDate.ed_id == ed_id).one_or_none()
    if not _examdate:
        raise HTTPException(status_code=404, detail="Data not found")
    ed_hour = time_difference(request.ed_start_time, request.ed_end_time)
    _examdate.ed_start_time = request.ed_start_time
    _examdate.ed_end_time = request.ed_end_time
    _examdate.ed_hour = ed_hour
    _examdate.ed_date = request.ed_date
    _examdate.ed_ready = request.ed_ready
    _examdate.ed_code = request.ed_code
    _examdate.active = request.active
    _examdate.update_date = todaytime()
    _examdate.vehicle_type_id = request.vehicle_type_id
    _examdate.branch_id = request.branch_id
    _examdate.school_id = request.school_id
    db.commit()
    return ResponseProcess(status="success", status_code="200", message="Success update data")


@router_course.get("/examdate/{school_id}", response_model=list[ExamDateRequestOutSchema])
def get_examdate(school_id: str, branch_id: str, vehicle_type_id: int, month: int, year: int, db: Session = Depends(get_db),  authenticated: bool = Depends(auth_request)):
    _examdate = db.query(ExamDate).order_by(asc(ExamDate.ed_date)).filter(ExamDate.cancelled == 1, extract(
        'year', ExamDate.ed_date) == year, extract('month', ExamDate.ed_date) == month)
    if branch_id != 'all':
        # โชว์เฉพาะสาขาตนเอง
        _examdate = _examdate.filter(ExamDate.branch_id == branch_id)
    else:
        _examdate = _examdate.filter(ExamDate.school_id == school_id)
      # แสดงข้อมูลโดยอิงประเภทยานพาหนะ
    if vehicle_type_id != 0:
      # โชว์วิชาอบรมเฉพาะสาขาตนเอง
        _examdate = _examdate.filter(
            ExamDate.vehicle_type_id == vehicle_type_id)
    else:
        _examdate = _examdate.filter(ExamDate.vehicle_type_id > 0)
    _examdate = _examdate.all()
    return _examdate


@router_course.delete("/examdate/{ed_id}")
def delete_examdate(ed_id: int, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _examdate = db.query(ExamDate).filter(
        ExamDate.ed_id == ed_id).one_or_none()
    if not _examdate:
        raise HTTPException(status_code=404, detail="Data not found")
    # db.delete(_examdate)
    _examdate.cancelled = 0
    db.commit()
    return ResponseProcess(status="success", status_code="200", message="Success delete data")
