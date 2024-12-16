import markdown
from fastapi import APIRouter, HTTPException, status, Header
from fastapi.responses import JSONResponse

from app.operation.CRUD import get_chat_history_from_db, verify_password_reset_token_and_get_email, \
    get_file_details_from_user_id, get_chat_history_using_file_id

chat_history_router = APIRouter(tags=["history"])


@chat_history_router.get("/chat/history")
async def chat_history_data(access_token: str = Header(default=None, convert_underscores=False)):
    final_answer_list = []
    final_response = None
    try:

        verify_user_response = verify_password_reset_token_and_get_email(access_toekn=access_token)
        if verify_user_response:

            chat_response = get_chat_history_from_db(verify_user_response.id)

            # get the answer and question
            for item in chat_response:
                html_response = markdown.markdown(item["answers"])
                question_answer_dict = {
                    "question": item["question"],
                    "response": html_response
                }
                final_answer_list.append(question_answer_dict)
            if final_answer_list:
                final_response = JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content=final_answer_list
                )
            else:
                final_response = JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
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


@chat_history_router.get("/file/history", status_code=status.HTTP_200_OK)
async def user_file_history(access_token: str = Header(default=None, convert_underscores=False)):
    final_response = None
    try:
        verify_user_response = verify_password_reset_token_and_get_email(access_toekn=access_token)
        if verify_user_response:
            file_response = get_file_details_from_user_id(user_id=verify_user_response.id)

            if file_response:
                response = {"file_id": file_response["file_id"], "file_location": file_response["file"],
                            "name": file_response["title"]}
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
                        "message": "Not found any file details for this user"

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


@chat_history_router.get("/file/chat/history/{file_id}", status_code=status.HTTP_200_OK)
async def user_chat_history_with_file(file_id: int,
                                      access_token: str = Header(default=None, convert_underscores=False)):
    final_response = None
    final_answer_list = []
    try:
        verify_user_response = verify_password_reset_token_and_get_email(access_toekn=access_token)
        if verify_user_response:
            response_chat_data = get_chat_history_using_file_id(file_id=file_id)
            if response_chat_data:
                for item in response_chat_data:
                    html_response = markdown.markdown(item["answers"])
                    question_answer_dict = {
                        "qa_id": item["qa_id"],
                        "question": item["question"],
                        "answers": html_response
                    }
                    final_answer_list.append(question_answer_dict)
                final_response = JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "cIntResponseStatus": status.HTTP_200_OK,
                        "cObjResponseData": final_answer_list
                    }
                )
            else:
                final_response = JSONResponse(
                    status_code=status.HTTP_204_NO_CONTENT,
                    content={
                        "cIntResponseStatus": status.HTTP_204_NO_CONTENT,
                        "message": "Not found any chat for this file"
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
