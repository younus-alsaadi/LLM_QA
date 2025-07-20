from fastapi import FastAPI, APIRouter
import os
base_router = APIRouter(
    prefix="/api/v1",
    tags=["api"],
    responses={404: {"description": "Not found"}},
)

@base_router.get("/")
async def welcome():
    app_name=os.getenv("APP_NAME")
    app_version=os.getenv("APP_VERSION")
    return {
        "app_Name" : app_name,
        "app_Version" : app_version,
    }