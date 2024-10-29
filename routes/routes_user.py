from fastapi import APIRouter, Depends, HTTPException
from passlib.hash import sha256_crypt
from sqlalchemy import desc, or_
from sqlalchemy.orm import Session, joinedload
from authen import auth_request
from database import get_db
from function import ceil, ternaryZero, todaytime, rows_limit
from models import User
from schemas_format.general_schemas import (FilterRequestSchema,
                                            ResponseData, ResponseProcess)
from schemas_format.user_schemas import UserLoginSchema, UserRequestInSchema, UserRequestOutSchema, UserRequestOutOptionSchema
router_user = APIRouter()


@router_user.post("/create")
def create_user(request: UserRequestInSchema, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _user = db.query(User).filter(
        User.username == request.username, User.school_id == request.school_id).one_or_none()
    if _user:
        raise HTTPException(status_code=404, detail="Username Error")
    password = request.password
    password_hash = sha256_crypt.encrypt(password)
    _user = User(
        username=request.username,
        password=password_hash,
        firstname=request.firstname,
        lastname=request.lastname,
        user_type=request.user_type,
        active=request.active,
        create_date=todaytime(),
        branch_id=request.branch_id,
        school_id=request.school_id
    )
    db.add(_user)
    db.commit()
    db.refresh(_user)
    return ResponseProcess(status="success", status_code="200", message="Success created data")


@router_user.post("/all")
def get_user(request: FilterRequestSchema, typeuser: str = "all", school_id: str = "all", branch_id: str = "all", db: Session = Depends(get_db),  authenticated: bool = Depends(auth_request)):
    skip = ternaryZero(((request.page - 1) * request.per_page))
    limit = rows_limit(request.per_page)
    search_value = request.search_value
    result = db.query(User).order_by(
        desc(User.create_date)).filter(User.cancelled == 1)
    if school_id == "all":
        result = result.filter(User.school_id != school_id)
    else:
        result = result.filter(User.school_id == school_id)

    if branch_id == "all":
        result = result.filter(User.branch_id != branch_id)
    else:
        result = result.filter(User.branch_id == branch_id)
    # # Filter user type : all , 1,2,3,4,5

    if typeuser == "1" or typeuser == "2" or typeuser == "3" or typeuser == "4" or typeuser == "5":
        result = result.filter(User.user_type == int(typeuser))
    else:
        result = result.filter(User.user_type > 0)

    total_data = result.count()

    if search_value:
        result = result.filter(or_(User.firstname.contains(search_value), User.lastname.contains(
            search_value), User.username.contains(search_value)))
    total_filter_data = result.count()
    result = result.offset(skip).limit(limit).all()
    total_page = ceil(total_data / request.per_page)
    content = [UserRequestOutSchema.from_orm(p) for p in result]
    return ResponseData(status="success", status_code="200", message="Success fetch all data", page=request.page, per_page=limit, total_page=total_page, total_data=total_data, total_filter_data=total_filter_data, data=content)


@router_user.get("/{user_id}", response_model=UserRequestOutSchema)
def get_by_user_id(user_id: str,  db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _user = db.query(User).filter(
        User.user_id == user_id, User.cancelled == 1).one_or_none()
    if not _user:
        raise HTTPException(status_code=404, detail="Data not found")
    return _user


@router_user.put("/{user_param}", response_model=UserRequestOutSchema)
def update_user(user_param: str, request: UserRequestInSchema,  db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):

    _userchk = db.query(User).filter(
        User.username == request.username, User.school_id == request.school_id, User.user_id != user_param, User.username != user_param).count()
    # print(_userchk)
    if _userchk > 0:
        raise HTTPException(status_code=404, detail="Username Error")

    _user = db.query(User).filter(
        or_(User.user_id == user_param, User.username == user_param), User.school_id == request.school_id).one_or_none()
    if not _user:
        raise HTTPException(status_code=404, detail="Data not found")
    password = request.password
    password_hash = sha256_crypt.encrypt(password)
    _user.username = request.username
    _user.password = password_hash
    _user.firstname = request.firstname
    _user.lastname = request.lastname
    _user.user_type = request.user_type
    _user.active = request.active
    _user.branch_id = request.branch_id
    _user.school_id = request.school_id

    db.commit()
    db.refresh(_user)
    return _user


@router_user.delete("/{user_id}")
def delete_user(user_id: str, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _user = db.query(User).filter(User.user_id == user_id).one_or_none()
    if not _user:
        raise HTTPException(status_code=404, detail="Data not found")
    # db.delete(_user)
    _user.cancelled = 0
    db.commit()
    return ResponseProcess(status="success", status_code="200", message="Success delete data")


@router_user.post("/login")
def login(request: UserLoginSchema, db: Session = Depends(get_db), authenticated: bool = Depends(auth_request)):
    _user = db.query(User).filter(
        User.username == request.username, User.cancelled == 1, User.school_id == request.school_id).first()
    if not _user:
        raise HTTPException(status_code=404, detail="Data not found")
    password = request.password

    # password = sha256_crypt.encrypt("password")
    chk_result = sha256_crypt.verify(password,  _user.password)

    if chk_result == True:
        return {
            "success": True,
            "user_id": _user.user_id,
            "user_type": _user.user_type,
            "full_name": str(_user.firstname) + " " + str(_user.lastname),
            "branch_id": _user.branch_id,
            "branch_name": _user.branch_user.branch_name,
            "school_id": _user.school_id,
            "school_name": _user.school_user.school_name,
        }
    else:
        raise HTTPException(status_code=404, detail="Data not found")
