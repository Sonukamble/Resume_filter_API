import os
from typing import Annotated

from fastapi import APIRouter, Request, UploadFile, File, Form, Header, HTTPException, status
from fastapi.responses import JSONResponse

from app.Configuration import Config
from app.operation.CRUD import verify_password_reset_token_and_get_email, save_file_in_db, \
    get_file_details_from_user_id, delete_file_using_file_id
from app.operation.FileProcessOperation import pdf_to_text

file_router = APIRouter()


@file_router.post("/upload/file/", status_code=status.HTTP_201_CREATED)
async def create_upload_file(
        request: Request,
        file: Annotated[UploadFile, File(description="A file read as UploadFile")],
        title: str = Form(...),
        access_token: str = Header(default=None, convert_underscores=False)
):
    final_response = None
    response_dict = None
    try:
        # Verify user and get email or user details
        verify_user_response = verify_password_reset_token_and_get_email(access_token)
        if verify_user_response:
            # Save file locally
            host_ip = request.client.host
            file_content = await file.read()
            file_location = f"{Config.TEMPORARY_FILE_PATH}\\{file.filename}"

            # Ensure directory exists
            os.makedirs(os.path.dirname(file_location), exist_ok=True)

            with open(file_location, "wb") as f:
                f.write(file_content)

            # convert pdf into text
            response_pdf_text = pdf_to_text(pdf_path=file_location)
            # Save file details in the database
            response = save_file_in_db(filepath=file_location, host_ip=host_ip, title=title, user=verify_user_response,
                                       pdf_text=response_pdf_text)

            # Convert response to a serializable format if needed
            # public_url = f"http://{request.client.host}:8000/files/{file.filename}"

            if response:
                response_dict = {"file_id": response.file_id, "file_location": response.file, "name": response.title}
                response_pdf_text_response = {"message": "Pdf uploaded successfully.", "file_data": response_dict}

                final_response = JSONResponse(
                    status_code=status.HTTP_201_CREATED,
                    content={
                        "cIntResponseStatus": status.HTTP_201_CREATED,
                        "cObjResponseData": response_pdf_text_response
                    }
                )
            else:
                final_response = JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={
                        "cIntResponseStatus": status.HTTP_500_INTERNAL_SERVER_ERROR,

                    }
                )
        else:
            final_response = JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "cIntResponseStatus": status.HTTP_401_UNAUTHORIZED,
                    "message": "Invalid or expired access token"
                }
            )
        return final_response
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        # Log the exception and raise a generic server error
        import logging
        logging.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@file_router.delete("/delete/files/{file_id}")
async def delete_uploaded_file(file_id: int, access_token: str = Header(default=None, convert_underscores=False)
                               ):
    final_response = None
    try:
        verify_user_response = verify_password_reset_token_and_get_email(access_token)
        if verify_user_response:
            # fetch data from the user_file table
            file_details = get_file_details_from_user_id(user_id=verify_user_response.id)

            if file_details:
                # get chat data
                deleted_file_response = delete_file_using_file_id(file_id=file_id)
                if deleted_file_response:
                    deleted_response = {"message": "File deleted successfully"}
                    final_response = JSONResponse(
                        status_code=status.HTTP_200_OK,
                        content={
                            "cIntResponseStatus": status.HTTP_200_OK,
                            "cObjResponseData": deleted_response
                        }
                    )
                else:
                    final_response = JSONResponse(
                        status_code=status.HTTP_404_NOT_FOUND,
                        content={
                            "cIntResponseStatus": status.HTTP_404_NOT_FOUND,
                            "message": "files not deleted from db"
                        }
                    )
            else:
                final_response = JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content={
                        "cIntResponseStatus": status.HTTP_404_NOT_FOUND,
                        "message": "files not found in db"
                    }
                )
        else:
            final_response = JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "cIntResponseStatus": status.HTTP_401_UNAUTHORIZED,
                    "message": "Invalid or expired access token"
                }
            )
        return final_response
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        # Log the exception and raise a generic server error
        import logging
        logging.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
