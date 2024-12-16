import os
from typing import Annotated

from fastapi import APIRouter, Request, UploadFile, File, Form, HTTPException, status
from fastapi.responses import JSONResponse

from app.Configuration import Config
from app.operation.FileProcessOperation import pdf_to_text
from app.without_auth_router.file_entity.CrudOperation import save_file_in_db_for_files, \
    create_question_entry_in_table, get_file_details_from_file_id, get_answer_from_gen_AI_without_auth, \
    delete_file_using_file_id_without_auth
from app.without_auth_router.file_entity.ModelEntity import QuestionBase

file_router_without_auth = APIRouter(tags=["Sample"])


@file_router_without_auth.post("/upload/file/Sample", status_code=status.HTTP_201_CREATED)
async def create_upload_file(
        request: Request,
        file: Annotated[UploadFile, File(description="A file read as UploadFile")],
        title: str = Form(...)
):
    final_response = None
    response_dict = None
    try:
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
        response = save_file_in_db_for_files(filepath=file_location, host_ip=host_ip, title=title,
                                             pdf_text=response_pdf_text)

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
        return final_response
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        # Log the exception and raise a generic server error
        import logging
        logging.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@file_router_without_auth.post("/upload/question/sample", status_code=status.HTTP_201_CREATED)
def create_question(question: QuestionBase):
    final_response = None
    try:
        # first check the file is present
        file_data_response = get_file_details_from_file_id(file_id_data=question.file_id)

        if file_data_response:
            # create entry in the user_questions table
            response_data = create_question_entry_in_table(question=question.question, file_id=question.file_id)
            if response_data:
                #     send data to the genAI
                final_updated = get_answer_from_gen_AI_without_auth(original_question=response_data["question"],
                                                                    original_file_text=file_data_response[
                                                                        "resume_text"])
                if final_updated:
                    final_response = JSONResponse(
                        status_code=status.HTTP_201_CREATED,
                        content={
                            "cIntResponseStatus": status.HTTP_201_CREATED,
                            "cObjResponseData": final_updated
                        }
                    )
                else:
                    final_response = JSONResponse(
                        status_code=status.HTTP_404_NOT_FOUND,
                        content={
                            "cIntResponseStatus": status.HTTP_404_NOT_FOUND,
                            "message": "Not get the answer"
                        }
                    )
            else:
                final_response = JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content={
                        "cIntResponseStatus": status.HTTP_404_NOT_FOUND,
                        "message": "Not get the answer"
                    }
                )
        else:
            final_response = JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "cIntResponseStatus": status.HTTP_404_NOT_FOUND,
                    "message": "entry is not created in table for question entry"
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


@file_router_without_auth.delete("/delete/files/sample/{file_id}")
async def delete_uploaded_file(file_id: int):
    final_response = None
    try:
        # fetch data from the user_file table
        file_details = get_file_details_from_file_id(file_id_data=file_id)

        if file_details:
            # get chat data
            deleted_file_response = delete_file_using_file_id_without_auth(file_id=file_details["file_id"])
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

        return final_response
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        # Log the exception and raise a generic server error
        import logging
        logging.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
