from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm

import models
from database import engine
from routes.routes_course import router_course
from routes.routes_general import router_general
from routes.routes_masterdata import router_masterdata
from routes.routes_register import router_register
from routes.routes_school import router_school
from routes.routes_teacher import router_teacher
from routes.routes_user import router_user

models.Base.metadata.create_all(bind=engine)
# app = FastAPI()
app = FastAPI(
    title="DTMS API",
    description="ระบบบริหารโรงเรียนสอนขับรถ",
    version="1.0",
    contact={
        "name": "Siwakorn Banluesapy",
        "email": "siwakorn167@gmail.com",
    }

)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# สำหรับเปิด Test Swagger UI


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    setuser = "siwakorn"
    # setpassword = "5CJwIvpNYwASgKUU"
    setpassword = "12345"
    username = form_data.username
    password = form_data.password
    # print(username)
    if username == setuser and password == setpassword:
        return {"access_token": "success", "token_type": "bearer"}
    else:
        raise HTTPException(
            status_code=400, detail="Incorrect username or password")


app.include_router(router_user, prefix="/user", tags=["User"])
app.include_router(router_school, prefix="/school", tags=["School"])
app.include_router(router_course, prefix="/course", tags=["Course"])
app.include_router(router_teacher, prefix="/teacher", tags=["Teacher"])
app.include_router(router_register, prefix="/register", tags=["Register"])
app.include_router(router_general, prefix="/general", tags=["General"])
app.include_router(router_masterdata, prefix="/masterdata",
                   tags=["Masterdata"])
