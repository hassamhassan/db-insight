from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship
from .base_model import BaseModel, BaseQueries


class DBCredentials(BaseModel):
    __tablename__ = "db_credentials"

    user_id = Column(String, ForeignKey("users.id"))
    database_engine = Column(String)
    database_name = Column(String)
    host = Column(String)
    db_user = Column(String)
    port = Column(Integer)
    password = Column(String)

    user = relationship("User", back_populates="db_credentials")


class TransactionMethods(BaseQueries):
    model = DBCredentials
