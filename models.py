from database import Base
from sqlalchemy import Column,Integer,String,Boolean,ForeignKey



class users(Base):
    __tablename__='todosapp'

    id=Column(Integer,primary_key=True,index=True)
    email=Column(String,unique=True)
    username=Column(String,unique=True)
    first_name=Column(String)
    last_name=Column(String)
    hashed_password=Column(String)
    is_active=Column(Boolean,default=True)
    role=   Column(String)


class todos(Base):
    __tablename__='todos'

    id=Column(Integer,primary_key=True,index=True)
    book=Column(String)
    description=Column(String)
    complete=Column(Boolean,default=False)
    is_owned=Column(Integer,ForeignKey("todosapp.id"))



