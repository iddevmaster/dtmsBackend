from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, or_
from sqlalchemy.orm import Session

from authen import auth_request
from database import get_db
from function import ceil, ternaryZero, todaytime
from models import Branch, School

from schemas_format.general_schemas import FilterRequestSchema,  ResponseProcess
from schemas_format.school_schemas import BranchRequestInSchema, BranchRequestOutSchema, BranchRequestOutOptionSchema, SchoolRequestInSchema, SchoolRequestOutSchema, SchoolRequestOutOptionSchema
router_school = APIRouter()


@router_school.post("/create")
async def create_school(request: SchoolRequestInSchema, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _school = School(
        school_name=request.school_name,
        active=request.active,
        create_date=todaytime(),
        update_date=todaytime()
    )
    db.add(_school)
    db.commit()
    db.refresh(_school)
    school_id = _school.school_id
    # สร้างสาขาขึ้นมา 1 สาขา
    _branch = Branch(
        branch_code="0",
        branch_name="สำนักงานใหญ่",
        active=1,
        create_date=todaytime(),
        update_date=todaytime(),
        school_id=school_id
    )
    db.add(_branch)
    db.commit()
    return ResponseProcess(status="success", status_code="200", message="Success created data")


@router_school.post("/all")
async def get_school(request: FilterRequestSchema, db: Session = Depends(get_db),  authenticated: bool = Depends(auth_request)):
    skip = ternaryZero(((request.page - 1) * request.per_page))
    limit = request.per_page
    search_value = request.search_value
    if search_value:
        result = db.query(School).filter(School.school_name ==
                                         search_value, School.cancelled == 1).offset(skip).limit(limit).all()
    else:
        result = db.query(School).order_by(desc(School.create_date)).filter(
            School.cancelled == 1).offset(skip).limit(limit).all()
    total_data = db.query(School).count()
    total_filter_data = len(result)
    total_page = ceil(total_data / request.per_page)
    return SchoolRequestOutOptionSchema(status="success", status_code="200", message="Success fetch all data", page=request.page, per_page=limit, total_page=total_page, total_data=total_data, total_filter_data=total_filter_data, data=result)


@router_school.get("/{school_id}", response_model=SchoolRequestOutSchema)
async def get_by_school_id(school_id: str,  db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _school = db.query(School).filter(
        School.school_id == school_id).one_or_none()
    if not _school:
        raise HTTPException(status_code=404, detail="Data not found")
    return _school


@router_school.put("/{school_id}")
async def update_school(school_id: str, request: SchoolRequestInSchema, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _school = db.query(School).filter(
        School.school_id == school_id).one_or_none()
    if not _school:
        raise HTTPException(status_code=404, detail="Data not found")
    _school.school_name = request.school_name
    _school.active = request.active
    _school.update_date = todaytime()

    db.commit()
    db.refresh(_school)
    return ResponseProcess(status="success", status_code="200", message="Success update data")


@router_school.delete("/{school_id}")
async def delete_school(school_id: str, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _school = db.query(School).filter(
        School.school_id == school_id).one_or_none()
    if not _school:
        raise HTTPException(status_code=404, detail="Data not found")
    _school.cancelled = 0
    # db.delete(_school)
    db.commit()
    db.refresh(_school)
    return ResponseProcess(status="success", status_code="200", message="Success delete data")


@router_school.post("/branch/create")
async def create_branch(request: BranchRequestInSchema, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _branch = Branch(
        branch_code=request.branch_code,
        branch_name=request.branch_name,
        active=request.active,
        create_date=todaytime(),
        update_date=todaytime(),
        school_id=request.school_id
    )
    db.add(_branch)
    db.commit()
    return ResponseProcess(status="success", status_code="200", message="Success created data")


@router_school.post("/branch/all/{school_id}")
async def get_branch(school_id: str, request: FilterRequestSchema, db: Session = Depends(get_db),  authenticated: bool = Depends(auth_request)):
    skip = ternaryZero(((request.page - 1) * request.per_page))
    limit = request.per_page
    search_value = request.search_value

    searchFilter = or_(Branch.branch_code.contains(search_value),
                       Branch.branch_name.contains(search_value))
    if search_value:
        result = db.query(Branch).order_by(desc(Branch.create_date)).filter(
            Branch.cancelled == 1, Branch.school_id == school_id, searchFilter).offset(skip).limit(limit).all()
    else:
        result = db.query(Branch).order_by(desc(Branch.create_date)).filter(
            Branch.cancelled == 1, Branch.school_id == school_id).offset(skip).limit(limit).all()
    total_data = db.query(Branch).filter(
        Branch.cancelled == 1, Branch.school_id == school_id).count()
    total_filter_data = len(result)
    total_page = ceil(total_data / request.per_page)
    return BranchRequestOutOptionSchema(status="success", status_code="200", message="Success fetch all data", page=request.page, per_page=limit, total_page=total_page, total_data=total_data, total_filter_data=total_filter_data, data=result)


@router_school.get("/branch/{branch_id}", response_model=BranchRequestOutSchema)
async def get_by_branch_id(branch_id: str,  db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _branch = db.query(Branch).filter(
        Branch.branch_id == branch_id).one_or_none()
    if not _branch:
        raise HTTPException(status_code=404, detail="Data not found")
    return _branch


@router_school.put("/branch/{branch_id}")
async def update_branch(branch_id: str, request: BranchRequestInSchema, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _branch = db.query(Branch).filter(
        Branch.branch_id == branch_id).one_or_none()
    if not _branch:
        raise HTTPException(status_code=404, detail="Data not found")
    _branch.branch_code = request.branch_code
    _branch.branch_name = request.branch_name
    _branch.active = request.active
    _branch.update_date = todaytime()
    _branch.school_id = request.school_id
    db.commit()
    # db.refresh(_branch)
    return ResponseProcess(status="success", status_code="200", message="Success update data")


@router_school.delete("/branch/{branch_id}")
async def delete_branch(branch_id: int, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _branch = db.query(Branch).filter(
        Branch.branch_id == branch_id).one_or_none()
    if not _branch:
        raise HTTPException(status_code=404, detail="Data not found")
    _branch.cancelled = 0
    db.commit()
    return ResponseProcess(status="success", status_code="200", message="Success delete data")
