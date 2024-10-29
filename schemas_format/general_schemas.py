from datetime import date, datetime, time
from typing import Generic, Optional, TypeVar, List
from pydantic.generics import GenericModel
from pydantic import BaseModel

T = TypeVar('T')


class ResponseProcess(GenericModel, Generic[T]):
    status: str
    status_code: str
    message: str


class ResponseData(GenericModel, Generic[T]):
    status: str
    status_code: str
    message: str
    page: int
    per_page: int
    total_page: int
    total_data: int
    total_filter_data: int
    data: List


class FilterRequestSchema(GenericModel, Generic[T]):
    page: Optional[int] = 1
    per_page: Optional[int] = 100
    search_value: Optional[str] = ""


class fullcalendarTypeAOutSchema(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    editable: Optional[bool] = None
    backgroundColor: Optional[str] = None

    class Config:
        orm_mode = True


class fullcalendarTypeBOutSchema(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None
    start: Optional[date] = None
    end: Optional[date] = None
    backgroundColor: Optional[str] = None

    class Config:
        orm_mode = True
