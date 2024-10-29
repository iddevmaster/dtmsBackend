from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy import and_, desc, or_
from sqlalchemy.orm import Session, joinedload

from authen import auth_request
from database import get_db
from function import (ceil, ternaryZero, todaytime)
from models import Teacher, TeacherIncome, TeacherLicense
from schemas_format.general_schemas import (
    FilterRequestSchema, ResponseProcess)
from schemas_format.teacher_schemas import TeacherIncomeRequestInSchema, TeacherIncomeRequestOutSchema, TeacherLicenceRequestInSchema, TeacherLicenceRequestOutSchema, TeacherRequestInSchema, TeacherRequestOutSchema, TeacherRequestOutOptionSchema

router_teacher = APIRouter()

# static file setup config
router_teacher.mount("/static", StaticFiles(directory="static"), name="static")


@router_teacher.post("/create")
def create_teacher(request: TeacherRequestInSchema, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _teacher = Teacher(
        teacher_prefix=request.teacher_prefix,
        teacher_firstname=request.teacher_firstname,
        teacher_lastname=request.teacher_lastname,
        teacher_id_number=request.teacher_id_number,
        teacher_gender=request.teacher_gender,
        teacher_phone=request.teacher_phone,
        teacher_email=request.teacher_email,
        teacher_cover=request.teacher_cover,
        active=request.active,
        create_date=todaytime(),
        update_date=todaytime(),
        branch_id=request.branch_id,
        school_id=request.school_id
    )
    db.add(_teacher)
    db.commit()
    db.refresh(_teacher)
    return ResponseProcess(status="success", status_code="200", message="Success created data")


@router_teacher.post("/{school_id}/all", )
def get_teacher(request: FilterRequestSchema, school_id: str, branch_id: str = "all",  db: Session = Depends(get_db),  authenticated: bool = Depends(auth_request)):
    skip = ternaryZero(((request.page - 1) * request.per_page))
    limit = request.per_page
    search_value = request.search_value
    if branch_id != 'all':
        # โชว์ครูเฉพาะสาขาตนเอง
        queryset = Teacher.branch_id == branch_id
    else:
        queryset = Teacher.school_id == school_id
    searchFilter = or_(Teacher.teacher_firstname.contains(search_value),
                       Teacher.teacher_lastname.contains(search_value),
                       Teacher.teacher_id_number.contains(search_value))

    # xpr = case([(Teacher.teacher_gender == 1, "ชาย"),
    #            (Teacher.teacher_gender == 2, "หญิง")], else_='-').label("gender_format")
    if search_value:
        result = db.query(Teacher).options(joinedload(Teacher.branch_teacher), joinedload(Teacher.school_teacher)).order_by(desc(Teacher.create_date)).filter(
            Teacher.cancelled == 1, queryset, searchFilter).offset(skip).limit(limit).all()
    else:
        result = db.query(Teacher).options(joinedload(Teacher.branch_teacher), joinedload(Teacher.school_teacher)).order_by(desc(Teacher.create_date)).filter(
            Teacher.cancelled == 1, queryset).offset(skip).limit(limit).all()
    total_data = db.query(Teacher).filter(
        Teacher.cancelled == 1, queryset).count()
    total_filter_data = len(result)
    total_page = ceil(total_data / request.per_page)

    # query = TeacherRequestInSchema.from_orm(result)
    # query = query.dict()
    return TeacherRequestOutOptionSchema(status="success", status_code="200", message="Success fetch all data", page=request.page, per_page=limit, total_page=total_page, total_data=total_data, total_filter_data=total_filter_data, data=result)


@router_teacher.get("/{teacher_id}", response_model=TeacherRequestOutSchema)
def get_by_teacher_id(teacher_id: str, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _teacher = db.query(Teacher).options(joinedload(Teacher.branch_teacher), joinedload(Teacher.school_teacher)).filter(
        Teacher.teacher_id == teacher_id).one_or_none()
    if not _teacher:
        raise HTTPException(status_code=404, detail="Data not found")
    return _teacher


@router_teacher.put("/{teacher_id}")
def update_teacher(teacher_id: str, request: TeacherRequestInSchema,  db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _teacher = db.query(Teacher).filter(
        Teacher.teacher_id == teacher_id).one_or_none()
    if not _teacher:
        raise HTTPException(status_code=404, detail="Data not found")
    _teacher.teacher_prefix = request.teacher_prefix
    _teacher.teacher_firstname = request.teacher_firstname
    _teacher.teacher_lastname = request.teacher_lastname
    _teacher.teacher_id_number = request.teacher_id_number
    _teacher.teacher_gender = request.teacher_gender,
    _teacher.teacher_phone = request.teacher_phone
    _teacher.teacher_email = request.teacher_email
    _teacher.teacher_cover = request.teacher_cover
    _teacher.active = request.active
    _teacher.update_date = todaytime(),
    _teacher.branch_id = request.branch_id
    _teacher.school_id = request.school_id

    db.commit()
    db.refresh(_teacher)
    return ResponseProcess(status="success", status_code="200", message="Success update data")


@router_teacher.delete("/{teacher_id}")
def delete_teacher(teacher_id: str, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _teacher = db.query(Teacher).filter(
        Teacher.teacher_id == teacher_id).one_or_none()
    if not _teacher:
        raise HTTPException(status_code=404, detail="Data not found")
    _teacher.cancelled = 0
    db.commit()
    return ResponseProcess(status="success", status_code="200", message="Success delete data")


@router_teacher.post("/licence/create")
def create_teacher_licence(request: TeacherLicenceRequestInSchema, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _teacher = db.query(TeacherLicense).filter(
        TeacherLicense.vehicle_type_id == request.vehicle_type_id, TeacherLicense.teacher_id == request.teacher_id).one_or_none()
    if not _teacher:
        _teacher = TeacherLicense(
            tl_number=request.tl_number,
            tl_level=request.tl_level,
            tl_date_of_expiry_staff=request.tl_date_of_expiry_staff,
            tl_date_of_issue=request.tl_date_of_issue,
            tl_date_of_expiry=request.tl_date_of_expiry,
            vehicle_type_id=request.vehicle_type_id,
            teacher_id=request.teacher_id
        )
        db.add(_teacher)
    else:
        raise HTTPException(status_code=404, detail="Data not found")

    db.commit()
    return ResponseProcess(status="success", status_code="200", message="Success created data")


@router_teacher.put("/licence/{tl_id}")
def update_teacher_licence(tl_id: int, request: TeacherLicenceRequestInSchema, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    validate_teacher = db.query(TeacherLicense).filter(
        TeacherLicense.vehicle_type_id == request.vehicle_type_id, TeacherLicense.teacher_id == request.teacher_id, TeacherLicense.tl_id != tl_id).one_or_none()
    if validate_teacher:
        raise HTTPException(status_code=404, detail="Data not found")
    _teacher = db.query(TeacherLicense).filter(
        TeacherLicense.tl_id == tl_id).one_or_none()
    if not _teacher:
        raise HTTPException(status_code=404, detail="Data not found")
    _teacher.tl_number = request.tl_number
    _teacher.tl_level = request.tl_level
    _teacher.tl_date_of_expiry_staff = request.tl_date_of_expiry_staff
    _teacher.tl_date_of_issue = request.tl_date_of_issue
    _teacher.tl_date_of_expiry = request.tl_date_of_expiry
    _teacher.vehicle_type_id = request.vehicle_type_id
    _teacher.teacher_id = request.teacher_id
    db.commit()
    return ResponseProcess(status="success", status_code="200", message="Success update data")


@router_teacher.get("/licence/{teacher_id}", response_model=list[TeacherLicenceRequestOutSchema])
def get_teacher_licence(teacher_id: str,  db: Session = Depends(get_db),  authenticated: bool = Depends(auth_request)):

    result = db.query(TeacherLicense).order_by(desc(TeacherLicense.tl_id)).filter(
        TeacherLicense.teacher_id == teacher_id).options(joinedload(TeacherLicense.teacher_teacherlicence)).all()
    return result


@router_teacher.get("/licence/{school_id}/all", response_model=list[TeacherRequestOutSchema])
def get_teacher_licence(school_id: str, tl_level: int, vehicle_type_id: int, branch_id: str = "all",  db: Session = Depends(get_db),  authenticated: bool = Depends(auth_request)):
    presentday = datetime.today().strftime('%Y-%m-%d')
    if branch_id != 'all':
        # โชว์ครูเฉพาะสาขาตนเอง
        queryset = Teacher.branch_id == branch_id
    else:
        queryset = Teacher.school_id == school_id
    # ประธาน
    if tl_level == 3:
        # ถ้าบัตรอนุญาตครูอยู่ที่ระดับ 3 ให้แสดงตามประเภทยานพาหนะ
        queryset2 = TeacherLicense.tl_level == 3
        queryset2a = TeacherLicense.vehicle_type_id == vehicle_type_id
        queryset2b = and_(TeacherLicense.tl_date_of_expiry_staff > presentday,
                          TeacherLicense.tl_date_of_expiry > presentday)
    # กรรมการ สามารถเลือกระดับ 3 และบัตรยานพาหนะอื่นๆ มาเป้นกรรมการได้
    elif tl_level == 2:
        # ถ้าบัตรอนุญาตครูอยู่ที่ระดับ 2 ให้แสดงข้อมูลระดับ 3 ไปด้วย
        queryset2 = or_(TeacherLicense.tl_level == 2,
                        TeacherLicense.tl_level == 3)
        queryset2a = TeacherLicense.vehicle_type_id > 0
        queryset2b = and_(TeacherLicense.tl_date_of_expiry_staff > presentday,
                          TeacherLicense.tl_date_of_expiry > presentday)
    elif tl_level == 1:
        # สอนปฏิบัติ - ทฤษฏี  เป็นกรรมการไม่ได้
        queryset2 = TeacherLicense.tl_level != 0
        queryset2a = TeacherLicense.vehicle_type_id == vehicle_type_id
        queryset2b = and_(TeacherLicense.tl_date_of_expiry_staff > presentday,
                          TeacherLicense.tl_date_of_expiry > presentday)
    else:
        #
        queryset2 = TeacherLicense.tl_level != 0
        queryset2a = TeacherLicense.vehicle_type_id > 0
        queryset2b = TeacherLicense.tl_id > 0
    result = db.query(Teacher).options(joinedload(Teacher.branch_teacher), joinedload(Teacher.school_teacher)).join(TeacherLicense, Teacher.teacher_id == TeacherLicense.teacher_id).order_by(desc(Teacher.create_date)).filter(
        queryset, queryset2, queryset2a, queryset2b,  Teacher.cancelled == 1).all()
    return result


@router_teacher.delete("/licence/{tl_id}")
def delete_teacher_licence(tl_id: int, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _teacher = db.query(TeacherLicense).filter(
        TeacherLicense.tl_id == tl_id).one_or_none()
    if not _teacher:
        raise HTTPException(status_code=404, detail="Data not found")
    db.delete(_teacher)
    db.commit()
    return ResponseProcess(status="success", status_code="200", message="Success delete data")


@router_teacher.post("/income/create")
def create_teacher_income(request: TeacherIncomeRequestInSchema, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):

    chkdata = db.query(TeacherIncome).filter(
        TeacherIncome.ti_amount_type == request.ti_amount_type, TeacherIncome.teacher_id == request.teacher_id,
        TeacherIncome.subject_learn_type == request.subject_learn_type, TeacherIncome.vehicle_type_id == request.vehicle_type_id
    ).one_or_none()

    #  ไม่อนุญาตให้ข้อมูลซ้ำกัน
    if chkdata:
        raise HTTPException(status_code=404, detail="Data not found")
    # ถ้ามีการเลือกเงินเดือน ให้เคลียร์ค่าตอบแทนอื่นๆ ทิ้ง
    # if request.ti_amount_type == 4:
    #     db.query(TeacherIncome).filter(
    #         TeacherIncome.teacher_id == request.teacher_id).delete()

    _teacher = TeacherIncome(
        ti_amount=request.ti_amount,
        ti_amount_type=request.ti_amount_type,
        ti_unit=request.ti_unit,
        ti_unit_type=request.ti_unit_type,
        subject_learn_type=request.subject_learn_type,
        vehicle_type_id=request.vehicle_type_id,
        teacher_id=request.teacher_id
    )
    db.add(_teacher)
    db.commit()
    return ResponseProcess(status="success", status_code="200", message="Success created data")


@router_teacher.put("/income/{ti_id}")
def update_teacher_income(ti_id: int, request: TeacherIncomeRequestInSchema, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):

    chkdata = db.query(TeacherIncome).filter(
        TeacherIncome.ti_amount_type == request.ti_amount_type, TeacherIncome.teacher_id == request.teacher_id,
        TeacherIncome.subject_learn_type == request.subject_learn_type, TeacherIncome.vehicle_type_id == request.vehicle_type_id,
        TeacherIncome.ti_id != ti_id
    ).one_or_none()
    #  ไม่อนุญาตให้ข้อมูลซ้ำกัน
    if chkdata:
        raise HTTPException(status_code=404, detail="Data not found")
    # ถ้ามีการเลือกเงินเดือน ให้เคลียร์ค่าตอบแทนอื่นๆ ทิ้ง
    # if request.ti_amount_type == 4:
    #     db.query(TeacherIncome).filter(
    #         TeacherIncome.teacher_id == request.teacher_id).delete()
    _teacher = db.query(TeacherIncome).filter(
        TeacherIncome.ti_id == ti_id).one_or_none()
    if not _teacher:
        raise HTTPException(status_code=404, detail="Data not found")
    _teacher.ti_amount = request.ti_amount
    _teacher.ti_amount_type = request.ti_amount_type
    _teacher.ti_unit = request.ti_unit
    _teacher.ti_unit_type = request.ti_unit_type
    _teacher.subject_learn_type = request.subject_learn_type
    _teacher.vehicle_type_id = request.vehicle_type_id
    _teacher.teacher_id = request.teacher_id
    db.commit()
    return ResponseProcess(status="success", status_code="200", message="Success update data")


@router_teacher.get("/income/{teacher_id}", response_model=list[TeacherIncomeRequestOutSchema])
def get_teacher_income(teacher_id: str,  db: Session = Depends(get_db),  authenticated: bool = Depends(auth_request)):
    result = db.query(TeacherIncome).order_by(desc(TeacherIncome.ti_id)).filter(
        TeacherIncome.teacher_id == teacher_id).options(joinedload(TeacherIncome.teacher_teacherincome)).all()
    return result


@router_teacher.delete("/income/{ti_id}")
def delete_teacher_income(ti_id: int, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _teacher = db.query(TeacherIncome).filter(
        TeacherIncome.ti_id == ti_id).one_or_none()
    if not _teacher:
        raise HTTPException(status_code=404, detail="Data not found")
    db.delete(_teacher)
    db.commit()
    return ResponseProcess(status="success", status_code="200", message="Success delete data")
