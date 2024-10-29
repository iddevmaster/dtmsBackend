
import base64
import os
import secrets
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
from pydantic import BaseModel
from sqlalchemy.orm import Session

from authen import auth_request
from data_common import base_system_url
from database import get_db
from function import create_directory

router_general = APIRouter()

# static file setup config
router_general.mount("/static", StaticFiles(directory="static"), name="static")
path = "static/"


class Item(BaseModel):
    file_path: str


class base64File(BaseModel):
    file_path: str
    file_name: str


@router_general.post("/upload/profile")
async def create_upload(school_id: str, file: UploadFile = File(...), authenticated: bool = Depends(auth_request)):
    # FILEPATH = "./static/images/"
    FILEPATH = create_directory("static/" + school_id + "/")
    filename = file.filename
    # extension = filename.split(".")[1]
    extension = filename.split(".").pop()
    if extension.lower() not in ["png", "jpg", "jpeg"]:
        raise HTTPException(
            status_code=404, detail="File extention not allowed")

    token_name = secrets.token_hex(10)+"."+extension
    generated_name = FILEPATH + token_name

    file_content = await file.read()
    with open(generated_name, "wb") as file:
        file.write(file_content)
    # PILLOW
    img = Image.open(generated_name)
    img = img.resize(size=(200, 200))
    img.save(generated_name)

    file.close()
    # ตัด static ออกเพื่อให้ url ภายนอกปลอดภัยยิ่งขึ้น
    use_path = str(generated_name.strip("static/"))
    file_path = base_system_url + "general/render/?file_path=" + use_path
    return {'file_name': token_name, 'file_path': use_path, "file_url": file_path}


@router_general.get("/render/")
async def get_file(file_path: str):
    use = os.path.join(path, file_path)
    if os.path.exists(use):
        return FileResponse(use)
    return {'message': 'File not found!'}


@router_general.delete("/remove/")
async def delete_file(file_path: str, authenticated: bool = Depends(auth_request)):
    use = os.path.join(path, file_path)
    if os.path.exists(use):
        file_to_rem = Path(use)
        file_to_rem.unlink()
        return {'message': 'Delete file success'}
    else:
        # print("The file does not exist")
        return {'message': 'The file does not exist'}


@router_general.post("/base64tofile/")
async def create_file(school_id: str, request: base64File):
    FILEPATH = create_directory("static/" + school_id + "/")
    file_name = request.file_name
    img_data = request.file_path
    generated_name = FILEPATH + file_name
    decoded_data = base64.b64decode((img_data))
    # write the decoded data back to original format in  file
    img_file = open(str(generated_name), 'wb')
    img_file.write(decoded_data)
    img_file.close()

    # ตัด static ออกเพื่อให้ url ภายนอกปลอดภัยยิ่งขึ้น
    use_path = str(generated_name.strip("static/"))
    file_path = base_system_url + "general/render/?file_path=" + use_path
    return {'file_name': file_name, 'file_path': use_path, "file_url": file_path}
