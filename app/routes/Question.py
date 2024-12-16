from fastapi import APIRouter, Header, HTTPException, status
from fastapi.responses import JSONResponse

from app.entity.PydanticModel import CreateQuestion
from app.operation.CRUD import verify_password_reset_token_and_get_email, craete_question_entry, \
    get_file_details_from_user_id, delete_chat_data
from app.operation.FileProcessOperation import get_answer_from_gen_AI

question_router = APIRouter(tags=["Question Data"])


@question_router.post("/upload/question", status_code=status.HTTP_201_CREATED)
def create_question(question: CreateQuestion,
                    access_token: str = Header(default=None, convert_underscores=False)
                    ):
    final_response = None
    try:
        # Verify user and get email or user details
        verify_user_response = verify_password_reset_token_and_get_email(access_token)
        if verify_user_response:
            # save the question in the table
            user_files = get_file_details_from_user_id(user_id=verify_user_response.id)

            # create entry in the user_questions table
            response_data = craete_question_entry(question=question.question, user_id=user_files["user_id"],
                                                  file_id=user_files["file_id"])

            # get the answer from file
            if response_data:
                #     get the answer from the db
                final_data = get_answer_from_gen_AI(original_question=response_data["question"],
                                                    original_file_text=user_files["resume_text"])
                if final_data:
                    final_response = JSONResponse(
                        status_code=status.HTTP_201_CREATED,
                        content={
                            "cIntResponseStatus": status.HTTP_201_CREATED,
                            "cObjResponseData": final_data
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


@question_router.delete("/delete/chat_ids/")
def delete_question_data(chat_ids: list[int], access_token: str = Header(default=None, convert_underscores=False)):
    final_response = None
    try:
        # Verify user and get email or user details
        verify_user_response = verify_password_reset_token_and_get_email(access_token)
        if verify_user_response:
            response = delete_chat_data(qa_id=chat_ids)
            if response:
                final_response = JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "cIntResponseStatus": status.HTTP_200_OK,
                        "cObjResponseData": response
                    }
                )
            else:
                final_response = JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content={
                        "cIntResponseStatus": status.HTTP_404_NOT_FOUND,
                        "message": "Not deleted the question"
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
