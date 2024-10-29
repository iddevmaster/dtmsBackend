
from typing import Optional
from pydantic import BaseModel


class ProvinceRequestOutSchema(BaseModel):
    province_code: Optional[int] = None
    province_name: Optional[str] = None

    class Config:
        orm_mode = True
