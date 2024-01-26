import uuid

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import ORJSONResponse
from sqlalchemy.orm import Session

from database.db import get_db
from models.user import UserMethods
from schemas.users_schema import (
    UserLoginRequestSchema,
    UserRegisterRequestSchema,
)
from utils.constants import (
    SUCCESS,
    NOT_FOUND,
    EMAIL_ALREADY_EXIST,
    INCORRECT_EMAIL_PASSWORD,
    USER_REGISTERED_SUCCESSFULLY,
)
from views.users import (
    create_access_token,
    authenticate_user, hash_password
)

user_router = APIRouter(
    prefix="/user",
    tags=["Users"],
    responses={404: {"description": NOT_FOUND}},
)


@user_router.post("/register")
async def register_user(
        user: UserRegisterRequestSchema,
        db: Session = Depends(get_db)
) -> ORJSONResponse:
    """
    Register new User.

    Args:
        user: UserRegisterRequestSchema - The user data to be registered.
        db: Database Session.

    Returns:
        Dict[str, str] (ORJSONResponse): A dictionary with a message indicating the registration status.
    """
    user_check = UserMethods.get_record_with_(db, email=user.email)
    if user_check:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=EMAIL_ALREADY_EXIST
        )
    user_data = user.model_dump()
    user_data["id"] = str(uuid.uuid4())
    user_data["password"] = hash_password(user.password.get_secret_value())
    UserMethods.create_record(user_data, db)
    db.commit()

    return ORJSONResponse(
        content={"message": USER_REGISTERED_SUCCESSFULLY},
        status_code=status.HTTP_201_CREATED
    )


@user_router.post("/login")
async def login_user(
        user: UserLoginRequestSchema,
        db: Session = Depends(get_db)
) -> ORJSONResponse:
    """
    Authenticate user login.

    Args:
        user: UserLoginRequestSchema - The user login credentials.
        db: Database Session.

    Returns:
        ORJSONResponse: A dictionary with a message and access token upon successful login.
    """
    user_data = await authenticate_user(
        db=db,
        email=user.email,
        password=user.password.get_secret_value(),
    )
    if not user_data:
        raise HTTPException(
            detail=INCORRECT_EMAIL_PASSWORD,
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    access_token = await create_access_token(data={"id": user_data.id, "email": user_data.email})
    token_data = {
        "status": SUCCESS,
        "access_token": access_token,
        "token_type": "bearer",
    }

    return ORJSONResponse(
        content={"data": token_data},
        status_code=status.HTTP_200_OK
    )
