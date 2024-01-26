import uuid
from datetime import datetime
from typing import Optional, Dict
from sqlalchemy import Column, DateTime, Boolean, String
from sqlalchemy.orm import Session

from database.db import Base


class BaseModel(Base):
    __abstract__ = True

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(
        DateTime, nullable=True, default=datetime.now, onupdate=datetime.now
    )
    is_active = Column(Boolean, nullable=False, default=True)


class BaseQueries:
    model: Optional = None

    @classmethod
    def get_record_with_id(cls, model_id: str, db: Session):
        return db.query(cls.model).filter(cls.model.id == model_id).first()

    @classmethod
    def get_record_with_(cls, db: Session, **kwargs):
        return db.query(cls.model).filter_by(**kwargs).first()

    @classmethod
    def get_all_record_with_(cls, db: Session, **kwargs):
        return db.query(cls.model).filter_by(**kwargs).all()

    @classmethod
    def get_all_records(cls, db: Session, limit=100, skip=0):
        return db.query(cls.model).offset(skip).limit(limit).all()

    @classmethod
    def create_record(cls, values: Dict, db: Session):
        obj = cls.model(**values)
        db.add(obj)
        db.flush()
        return obj

    @classmethod
    def update_record(cls, db: Session, record_id: str, update_data: Dict):
        return db.query(cls.model).filter(cls.model.id == record_id).update(update_data)
