from fastapi import APIRouter, Depends,status,HTTPException
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

routers=APIRouter()

def get_db():
    db=sessionLocal()
    try:
        yield db

    finally:
        db.close()

db_dep=Annotated[Session,Depends(get_db)]
user_dependency=Annotated[dict,Depends(get_current_user)]

@routers.get('/')
def list(db:db_dep):  #data injection
    return db.query(todos).all()


@routers.get('/todo/{id}',status_code=status.HTTP_200_OK)
async def read(db:db_dep):
    todo_model=db.query(todos).filter(todos.id ==id).first()
    if todo_model is not None:
        return  todo_model
    raise HTTPException(status_code=404,detail="NOT found")


class TODO(BaseModel):
    book:str
    description:str
    complete:bool

@routers.post("/todo",status_code=status.HTTP_201_CREATED)
async def create(user:user_dependency,db:db_dep,Todo_request:TODO):
    if user is None:
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user')

    todo_model=todos(**Todo_request.model_dump(),is_owned=user['id'])
    db.add(todo_model)
    db.commit()
    return "success"


@routers.put("/todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def update(db:db_dep,todo_id:int,todo_request:TODO):
    todo_model=db.query(todos).filter(todos.id==todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404,detail="NOT FOUND")
    
    todo_model.book=todo_request.book
    todo_model.description=todo_request.description
    todo_model.complete=todo_request.complete

    db.add(todo_model)
    db.commit()
    return 'success'


@routers.delete('/todos/delete/{id}',status_code=status.HTTP_204_NO_CONTENT)
async def delete(db:db_dep,id:int):
    todo_model=db.query(todos).filter(todos.id==id).first()
    if todo_model is None:
        raise HTTPException(status_code=204,detail="NOT FOUND")
    db.query(todos).filter(todos.id==id).delete()

    db.commit()

