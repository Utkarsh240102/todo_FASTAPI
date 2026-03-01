from fastapi import APIRouter, Depends,status,HTTPException,Path
from pydantic import BaseModel,Field
from typing import Annotated
import models
from models import todos
from fastapi import FastAPI,Depends
from typing import Annotated
import models
from sqlalchemy.orm import Session
from models import todos
from database import engine,sessionLocal
from .auth import get_current_user

routers=APIRouter(
        prefix='/admin',
        tags=['admin']
)

def get_db():
    db=sessionLocal()
    try:
        yield db

    finally:
        db.close()

db_dep=Annotated[Session,Depends(get_db)]
user_dependency=Annotated[dict,Depends(get_current_user)]


@routers.get("/todo",status_code=status.HTTP_200_OK)
async def read_all(user:user_dependency,db:db_dep):
    if user is None or user.get('user_role')!='admin':
        raise HTTPException(status_code=401,detail='Authentication failed')
    return db.query(todos).all()


@routers.delete("/todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user:user_dependency,db:db_dep,todo_id:int=Path(gt=0)):
    if user is None or user.get('user_role')!='admin':
        raise HTTPException(status_code=401,detail='Authentication failed')
    todo_model=db.query(todos).filter(todos.id==todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404,detail='Todo not found')
    db.query(todos).filter(todos.id==todo_model.id).delete()
    db.commit()
    