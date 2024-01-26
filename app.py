from typing import Dict

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from routes.users import user_router
from routes.db_operations import db_operations_router
from utils.constants import APP_TITLE
from utils.openapi_tags_metadata import tags_metadata
from views.users import verify_user

app = FastAPI(
    title=APP_TITLE,
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=tags_metadata,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/ping", tags=["Health"])
async def health_check() -> Dict:
    """
    Health Check Endpoint.

    Returns:
        Dict
    """
    return {"message": "pong"}


app.include_router(user_router)
app.include_router(db_operations_router, dependencies=[Depends(verify_user)])
