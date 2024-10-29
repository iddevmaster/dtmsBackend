from typing import Optional

import requests
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import and_,  or_
from sqlalchemy.orm import Session

from authen import auth_request
from data_common import (base_branch_id, base_school_id, course_group,
                         vehicle_type)
from database import get_db
from function import ceil, ternaryZero, todaytime, rows_limit
from models import Branch, Country, ExamDate, LocationThai, School
from schemas_format.general_schemas import (FilterRequestSchema,
                                            ResponseData)

router_masterdata = APIRouter()


class locationFilter(BaseModel):
    district_name: Optional[str] = None
    amphur_name: Optional[str] = None
    province_name: Optional[str] = None


@router_masterdata.get("/install_default_data")
def install_default_data(db: Session = Depends(get_db)):
    # ข้อมูลประเทศ
    total_country = db.query(Country).count()
    status_country = False
    # ข้อมูลจังหวัด ตำบล อำเภอ ประเทสไทย
    total_location_thai = db.query(LocationThai).count()
    status_location_thai = False
    # ข้อมูลโรงเรียน
    check_school = db.query(School).filter(
        School.school_id == base_school_id).count()
    status_school = False
    # ข้อมูลสาขา
    check_branch = db.query(Branch).filter(
        Branch.branch_id == base_branch_id).count()
    status_branch = False
    # ข้อมูลวันสอบ
    check_examdate = db.query(ExamDate).filter(
        ExamDate.branch_id == base_branch_id).count()
    status_examdate = False
    if check_school <= 0:
        _school = School(
            school_id=base_school_id,
            school_name="ศูนย์กลาง",
            active=1,
            cancelled=0,
            create_date=todaytime(),
            update_date=todaytime()
        )
        db.add(_school)
        db.commit()
        status_school = True
    if check_branch <= 0:
        _branch = Branch(
            branch_id=base_branch_id,
            branch_code="center",
            branch_name="ศูนย์กลาง",
            active=1,
            cancelled=0,
            create_date=todaytime(),
            update_date=todaytime(),
            school_id=base_school_id
        )
        db.add(_branch)
        db.commit()
        status_branch = True
    if check_examdate <= 0:
        _examdate = ExamDate(
            ed_id=1,
            ed_start_time="08:00:00",
            ed_end_time="12:00:00",
            ed_hour=4,
            ed_date="2022-10-20",
            ed_ready=1,
            ed_code="center",
            active=1,
            cancelled=0,
            create_date=todaytime(),
            update_date=todaytime(),
            vehicle_type_id=1,
            branch_id=base_branch_id,
            school_id=base_school_id
        )
        db.add(_examdate)
        db.commit()
        status_examdate = True
    if total_country <= 0:
        api_url_country = "https://masterdata.thaionzon.com/country"
        response_country = requests.get(api_url_country)
        list_country = response_country.json()
        obj = []
        for row_country in list_country:
            # print(row_country["country_name_th"])
            _country = Country(
                country_name_th=str(
                    row_country["country_name_th"]).strip(),
                country_name_eng=str(
                    row_country["country_name_eng"]).strip(),
                country_official_name_th=str(
                    row_country["country_official_name_th"]).strip(),
                country_official_name_eng=str(
                    row_country["country_official_name_eng"]).strip(),
                capital_name_th=str(
                    row_country["capital_name_th"]).strip(),
                capital_name_eng=str(
                    row_country["capital_name_eng"]).strip(),
                zone=str(row_country["zone"]).strip(),
            )
            obj.append(_country)
        db.add_all(obj)
        db.commit()
        status_country = True
    if total_location_thai <= 0:
        api_url_location_thai = "https://masterdata.thaionzon.com/all_location"
        response_location_thai = requests.get(api_url_location_thai)
        list_location_thai = response_location_thai.json()
        obj = []
        for row_location_thai in list_location_thai:
            _location_thai = LocationThai(
                district_code=str(
                    row_location_thai["district_code"]).strip(),
                district_name=str(
                    row_location_thai["district_name"]).strip(),
                zipcode=str(
                    row_location_thai["zipcode"]).strip(),
                amphur_code=str(
                    row_location_thai["amphur_code"]).strip(),
                amphur_name=str(
                    row_location_thai["amphur_name"]).strip(),
                province_code=str(
                    row_location_thai["province_code"]).strip(),
                province_name=str(row_location_thai["province_name"]).strip(),
            )
            obj.append(_location_thai)
        db.add_all(obj)
        db.commit()
        status_location_thai = True

    return {"country": status_country, "location_thai": status_location_thai, "school": status_school, "branch": status_branch, "examdate": status_examdate}


@router_masterdata.get("/course_group")
def general_course_group():
    # for k in course_group:
    return course_group


@router_masterdata.get("/vehicle_type")
def general_vehicle_type():
    # for k in course_group:
    return vehicle_type


@router_masterdata.post("/location")
def general_location(request: FilterRequestSchema, db: Session = Depends(get_db)):
    skip = ternaryZero(((request.page - 1) * request.per_page))
    limit = rows_limit(request.per_page)
    search_value = request.search_value
    _location = db.query(LocationThai)
    total_data = _location.count()
    # ค้นหาปกติ
    if search_value:
        _location = _location.filter(or_(LocationThai.zipcode.contains(search_value),
                                         LocationThai.amphur_name.contains(
                                             search_value),
                                         LocationThai.district_name.contains(
                                             search_value),
                                         LocationThai.province_name.contains(search_value)))
    total_filter_data = _location.count()
    _location = _location.offset(skip).limit(limit).all()
    total_page = ceil(total_data / request.per_page)
    return ResponseData(status="success", status_code="200", message="Success fetch all data", page=request.page, per_page=limit, total_page=total_page, total_data=total_data, total_filter_data=total_filter_data, data=_location)


@router_masterdata.post("/country")
def general_country(request: FilterRequestSchema, db: Session = Depends(get_db)):
    skip = ternaryZero(((request.page - 1) * request.per_page))
    limit = rows_limit(request.per_page)
    search_value = request.search_value
    _country = db.query(Country)
    total_data = _country.count()
    # ค้นหาปกติ
    if search_value:
        _country = _country.filter(or_(Country.country_name_th.contains(search_value),
                                       Country.country_name_eng.contains(
                                           search_value),
                                       Country.country_official_name_th.contains(
                                           search_value),
                                       Country.capital_name_th.contains(
                                           search_value),
                                       Country.capital_name_eng.contains(search_value)))
    total_filter_data = _country.count()
    _country = _country.offset(skip).limit(limit).all()
    total_page = ceil(total_data / request.per_page)
    return ResponseData(status="success", status_code="200", message="Success fetch all data", page=request.page, per_page=limit, total_page=total_page, total_data=total_data, total_filter_data=total_filter_data, data=_country)


@router_masterdata.post("/location/filter")
def general_location_filter(request: locationFilter, db: Session = Depends(get_db)):
    # ค้นหาปกติ
    _location = db.query(LocationThai).filter(
        and_(LocationThai.amphur_name.contains(request.amphur_name),
             LocationThai.district_name.contains(
            request.district_name),
            LocationThai.province_name.contains(request.province_name))).one_or_none()
    if not _location:
        raise HTTPException(status_code=404, detail="Data not found")
    return _location
