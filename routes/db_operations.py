from typing import List, Union

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import ORJSONResponse
from sqlalchemy.orm import Session

from sqlalchemy import create_engine, inspect

from database.db import get_db
from models import User
from models.db_credentials import TransactionMethods, DBCredentials
from schemas.db_operations import DBCredentialsCreateSchema, DBCredentialsSchema, DatabaseSchemaInfo, TableInfo
from utils.constants import NOT_FOUND
from views.users import verify_user

db_operations_router = APIRouter(
    prefix="/db",
    tags=["Database Operations"],
    responses={404: {"description": NOT_FOUND}},
)


@db_operations_router.post("/create-credentials")
async def create_db_credentials(
        db_credentials: DBCredentialsCreateSchema,
        db: Session = Depends(get_db),
        current_user: User = Depends(verify_user),
) -> ORJSONResponse:
    """
    Create new database credentials.

    Args:
        db_credentials: DBCredentialsCreateSchema - The database credentials data to be created.
        db: Database Session.
        current_user: User - The current logged-in User details.

    Returns:
        Dict[str, str] (ORJSONResponse): A dictionary with a message indicating the creation status.
    """
    db_credentials_data = db_credentials.model_dump()
    db_credentials_data["user_id"] = current_user.id
    db_credentials_data["password"] = db_credentials.password.get_secret_value()

    # Additional validation and business logic can be added as needed
    TransactionMethods.create_record(db_credentials_data, db)
    db.commit()

    return ORJSONResponse(
        content={"message": "Database credentials created successfully"},
        status_code=status.HTTP_201_CREATED,
    )


@db_operations_router.get("/get-all-credentials", response_model=list[DBCredentialsSchema])
async def get_all_db_credentials(
        db: Session = Depends(get_db),
        current_user: User = Depends(verify_user),
) -> List[DBCredentials]:
    """
    Get all database credentials.

    Args:
        db: Database Session.
        current_user: User - The current logged-in User details.

    Returns:
        List[DBCredentials]: A list of database credentials.
    """
    db_credentials_list = TransactionMethods.get_all_record_with_(db, user_id=current_user.id)

    if not db_credentials_list:
        raise HTTPException(
            detail="No database credentials found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return db_credentials_list


@db_operations_router.get("/get-database-schema", response_model=DatabaseSchemaInfo)
async def get_database_schema(
    database_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_user),
) -> DatabaseSchemaInfo:
    """
    Retrieve database schema information.

    Args:
        database_id: ID of the database credentials.
        db: Database Session.
        current_user: User - The current logged-in User details.

    Returns:
        DatabaseSchemaInfo: Database schema information.
    """
    db_credentials = TransactionMethods.get_record_with_id(db=db, model_id=database_id)  # NoQa

    if not db_credentials or db_credentials.user_id != current_user.id:
        raise HTTPException(
            detail="Database credentials not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    # Create a SQLAlchemy engine using the retrieved credentials
    database_engine = create_engine(
        f"{db_credentials.database_engine}://{db_credentials.db_user}:{db_credentials.password}@"
        f"{db_credentials.host}:{db_credentials.port}/{db_credentials.database_name}",
    )

    inspector = inspect(database_engine)

    # Extract database schema information
    database_info = DatabaseSchemaInfo(database_name=db_credentials.database_name, tables=[])

    for table_name in inspector.get_table_names():
        columns_info = []

        for column in inspector.get_columns(table_name):
            column_info = {
                "name": column["name"],
                "type": str(column["type"]),
                "nullable": column["nullable"],
                "default": column["default"]
            }
            columns_info.append(column_info)

        table_info = TableInfo(table_name=table_name, columns=columns_info)
        database_info.tables.append(table_info)

    return database_info


@db_operations_router.get("/search-table", response_model=Union[TableInfo, None])
async def search_table(
    database_id: str,
    table_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_user),
) -> Union[TableInfo, None]:
    """
    Search for a table name within a database.

    Args:
        database_id: ID of the database credentials.
        table_name: Name of the table to search for.
        db: Database Session.
        current_user: User - The current logged-in User details.

    Returns:
        Union[TableInfo, None]: Table information if found, else None.
    """
    db_credentials = TransactionMethods.get_record_with_id(db=db, model_id=database_id)  # Noqa

    if not db_credentials or db_credentials.user_id != current_user.id:
        raise HTTPException(
            detail="Database credentials not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    # Create a SQLAlchemy engine using the retrieved credentials
    database_engine = create_engine(
        f"{db_credentials.database_engine}://{db_credentials.db_user}:{db_credentials.password}@"
        f"{db_credentials.host}:{db_credentials.port}/{db_credentials.database_name}",
    )

    inspector = inspect(database_engine)

    if table_name in inspector.get_table_names():
        columns_info = []

        for column in inspector.get_columns(table_name):
            column_info = {
                "name": column["name"],
                "type": str(column["type"]),
                "nullable": column["nullable"],
                "default": column["default"]
            }
            columns_info.append(column_info)

        return TableInfo(table_name=table_name, columns=columns_info)
