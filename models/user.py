from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from .base_model import BaseModel, BaseQueries


class User(BaseModel):
    __tablename__ = "users"

    email = Column(String, unique=True, index=True)
    password = Column(String)

    db_credentials = relationship("DBCredentials", back_populates="user")


class UserMethods(BaseQueries):
    model = User
