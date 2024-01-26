from typing import List, Any

from pydantic import BaseModel, SecretStr, field_validator


class DBCredentialsCreateSchema(BaseModel):
    database_engine: str
    database_name: str
    host: str
    db_user: str
    port: int
    password: SecretStr

    @field_validator("port")
    def validate_port(cls, value):
        if not (0 < value <= 9999):
            raise ValueError("Port must be an integer between 0000 and 9999")
        return value


class DBCredentialsSchema(BaseModel):
    id: str
    user_id: str
    database_engine: str
    database_name: str
    host: str
    db_user: str
    port: int
    password: SecretStr

    class Config:
        from_attributes = True


class ColumnInfo(BaseModel):
    name: str
    type: str
    nullable: bool
    default: Any


class TableInfo(BaseModel):
    table_name: str
    columns: List[ColumnInfo]


class DatabaseSchemaInfo(BaseModel):
    database_name: str
    tables: List[TableInfo]
