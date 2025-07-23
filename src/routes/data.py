from fastapi import APIRouter, Depends,UploadFile,status,Request
from fastapi.responses import JSONResponse
from numpy.core.records import record

from src.helpers.config import get_settings, Settings
from src.controllers import DataController, ProjectController,ProcessController
import aiofiles
from src.models import ResponseSignalEnum
import logging
from .schemes.data_scheme import ProcessRequest
from src.models.ProjectModel import ProjectModel
from src.models.ChunkModel import ChunkModel
from src.models.AssetModel import AssetModel
from src.models.db_schemes import DataChunk, Asset
from src.models.enum.AssetTypeEnum import AssetTypeEnum
import os
from bson.objectid import ObjectId

logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1","data"],
)

@data_router.post("/upload/{project_id}")
async def upload_data(request:Request,project_id: str, file: UploadFile, app_settings: Settings = Depends(get_settings)):

    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)

    project=await project_model.get_project_or_create_one(project_id=project_id)



    data_controller=DataController()

    id_valid, result_single = data_controller.validate_uploaded_file(file=file)
    if not id_valid:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=
        {"response":result_single})



    project_dir_path=ProjectController().get_project_path(project_id=project_id)
    file_path,file_id=data_controller.generate_unique_filepath(orig_file_name=file.filename,project_id=project_id)

    try:
        async with aiofiles.open(file_path, 'wb') as f:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)


    except Exception as e:

        logger.error(f"Error while uploading file: {e} to file {file_path}")


        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignalEnum.FILE_UPLOAD_FAILED.value
            }
        )
    #store the assets in the databaes

    asset_model=await AssetModel.create_instance(db_client=request.app.db_client)

    asset_resource=Asset(
        asset_project_id=project.id,
        asset_type=AssetTypeEnum.FILE.value,
        asset_name=file_id,
        asset_size=os.path.getsize(file_path)

    )

    asset_record=await asset_model.create_asset(asset=asset_resource)

    return JSONResponse(
        content={
            "signal": ResponseSignalEnum.FILE_UPLOAD_SUCCESS.value,
            "file_id": str(asset_record.id),
        }
    )

@data_router.post("/process/{project_id}")
async def process_endpoint(request:Request,project_id: str, process_request: ProcessRequest):

    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset=process_request.do_reset

    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)

    project = await project_model.get_project_or_create_one(project_id=project_id)

    asset_model = await AssetModel.create_instance(db_client=request.app.db_client)

    project_files_ids={}
    if process_request.file_id:
        asset_record=await asset_model.get_one_asset_record(
            asset_project_id=project.id,
            asset_name=process_request.file_id,
        )

        if asset_record is None:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignalEnum.FILE_ID_ERROR.value,
                }
            )

        project_files_ids = {
            asset_record.id[0] if isinstance(asset_record.id, tuple) else asset_record.id: asset_record.asset_name
        }
    else:

        project_files=await asset_model.get_all_project_assets(
            asset_project_id=project.id,
            asset_type=AssetTypeEnum.FILE.value)

        project_files_ids = {
            record_project.id if isinstance(record_project.id, tuple) else record_project.id: record_project.asset_name
            for record_project in project_files
        }

    if len(project_files_ids) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignalEnum.NO_FILES_ERROR.value,
            }
        )

    process_controller=ProcessController(project_id=project_id)

    no_records=0
    no_files=0

    chunk_model = await ChunkModel.create_instance(db_client=request.app.db_client)

    if do_reset == 1:
        _ = await chunk_model.delete_chunks_by_project_id(
            project_id=project.id
        )

    logger.debug(f"len(project_files_ids)={len(project_files_ids)}")

    for asset_id, file_id in project_files_ids.items():

        logger.debug(f"asset_id type = {type(asset_id)}, value = {asset_id} || file_id = {file_id}")

        file_content=process_controller.get_file_content(file_id=file_id)

        if file_content is None:
            logger.error(f"File {file_id} has no content")
            continue


        file_chunks=process_controller.process_file_content(
            file_content=file_content,
            file_id=file_id,
            chunk_size=chunk_size,
            overlap_size=overlap_size,
        )

        if file_chunks is None or len(file_chunks) == 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignalEnum.PROCESSING_FAILED.value
                }
            )



        file_chunks_records = [
            DataChunk(
                chunk_text=chunk.page_content,
                chunk_metadata=chunk.metadata,
                chunk_order=i + 1,
                chunk_project_id=project.id,
                chunk_asset_id=asset_id
            )
            for i, chunk in enumerate(file_chunks)
        ]



        no_records += await chunk_model.insert_many_chunks(chunks=file_chunks_records)
        no_files+=1

    return JSONResponse(
        content={
            "signal": ResponseSignalEnum.PROCESSING_SUCCESS.value,
            "number_inserted_chunks": no_records,
            "number_processed_files": no_files
        }
    )



