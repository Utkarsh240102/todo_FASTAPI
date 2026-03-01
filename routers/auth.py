from fastapi import APIRouter,Depends,status,HTTPException
from datetime import timedelta,timezone
from pydantic import BaseModel
import datetime
from models import users
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import engine,sessionLocal
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from jose import jwt,JWTError

SECRET_KEY='A7K9X2M4Q8Z1L5R3T6Y0P2V9B4N8C1D7'
ALGORITHM='HS256'

router=APIRouter(
    prefix='/auth',
    tags=['auth']
)

def get_db():
    db=sessionLocal()
    try:
        yield db

    finally:
        db.close()

db_dep=Annotated[Session,Depends(get_db)]


bcrypt_context=CryptContext(schemes=['bcrypt'],deprecated='auto')
oauth2_bearer=OAuth2PasswordBearer(tokenUrl='auth/token')

def Authenticate_user(username:str,password:str,db):
    user=db.query(users).filter(users.username==username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password,user.hashed_password):
        return False
    return user


class CreateuserRequest(BaseModel):
    username:str
    email:str
    firstname:str
    lastname:str
    password:str
    role:str


class Token(BaseModel):
    access_token:str
    token_type:str

def create_access_token(username:str,user_id:int,expires_delta:timedelta):
    encode={'sub':username ,'id':user_id}
    expires=datetime.datetime.now(timezone.utc) + expires_delta
    encode.update({'exp':expires})
    return jwt.encode(encode,SECRET_KEY,algorithm=ALGORITHM)

async def get_current_user(token:Annotated[str,Depends(oauth2_bearer)]):
    try:
        playload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username:str=playload.get('sub')
        user_id:int=playload.get('id')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user')
        return {'username':username,'id':user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user')




@router.post('/',status_code=status.HTTP_201_CREATED)
async def auth(db:db_dep,request:CreateuserRequest):
    # Check if user already exists
    existing_user = db.query(users).filter(
        (users.username == request.username) | (users.email == request.email)
    ).first()
    
    if existing_user:
        return {"error": "Username or email already exists"}
    
    model=users(
        email=request.email,
        username=request.username,
        first_name=request.firstname,
        last_name=request.lastname,
        hashed_password=bcrypt_context.hash(request.password),
        is_active=True,
        role=request.role
    )

    db.add(model)
    db.commit()
    return "success"


@router.post('/token',response_model=Token)
async def login_for_access_roken(form_data:Annotated[OAuth2PasswordRequestForm,Depends()],db:db_dep):
    user =Authenticate_user(form_data.username,form_data.password,db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user')

    token=create_access_token(user.username,user.id,timedelta(minutes=20))

    return {'access_token':token,'token_type':'Bearer'}
    