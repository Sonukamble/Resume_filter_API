from datetime import datetime

from fastapi import HTTPException

from app.Configuration import Config
from app.operation.GoogleAI import google_gen_AI_response
from app.without_auth_router.file_entity.DBConnection import get_db
from app.without_auth_router.file_entity.ModelEntity import UserFilesData, FileQuestions


def save_file_in_db_for_files(filepath: str, host_ip: str, title: str, pdf_text: str):
    try:
        db = next(get_db())
        date_time = datetime.utcnow()

        user_file = UserFilesData(title=title, file=filepath, host_ip=host_ip, resume_text=pdf_text,
                                  created_at=date_time)

        # Add the user to the session and commit
        db.add(user_file)
        db.commit()

        # Refresh the instance to get updated data
        db.refresh(user_file)  # This line is fixed here
        return user_file
    except Exception as e:
        # Rollback and log other exceptions
        if db:
            db.rollback()
        print(f"An error occurred while updating user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

    finally:
        # Close the session
        if db:
            db.close()


def create_question_entry_in_table(question: str, file_id: int):
    response_entry = None
    try:
        db = next(get_db())

        question_entry = FileQuestions(question=question, file_id=file_id)

        db.add(question_entry)
        db.commit()
        # Refresh the instance to get updated data
        db.refresh(question_entry)  # This line is fixed here
        if question_entry:
            response_entry = {"question_id": question_entry.question_id, "question": question_entry.question, \
                              "file_id": question_entry.file_id}
        return response_entry
    except Exception as e:
        # Rollback and log other exceptions
        if db:
            db.rollback()
        print(f"An error occurred while updating user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

    finally:
        # Close the session
        if db:
            db.close()


def get_file_details_from_file_id(file_id_data: int):
    file_details_response = None
    try:
        db = next(get_db())

        file_details = db.query(UserFilesData).filter(UserFilesData.file_id == file_id_data).first()

        if file_details:
            file_details_response = {"file_id": file_details.file_id, "title": file_details.title, \
                                     "file": file_details.file, "resume_text": file_details.resume_text, \
                                     "host_ip": file_details.host_ip}
        return file_details_response
    except Exception as e:
        # Rollback and log other exceptions
        if db:
            db.rollback()
        print(f"An error occurred while updating user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

    finally:
        # Close the session
        if db:
            db.close()


def update_answer_in_table_without_auth(question_data: str, answer_data: str):
    response_data = None
    try:
        db = next(get_db())

        answer_response = db.query(FileQuestions).filter(FileQuestions.question == question_data).first()
        answer_response.answers = answer_data
        db.commit()
        db.refresh(answer_response)
        if answer_response:
            response_data = {"question_id": answer_response.question_id, "question": answer_response.question, \
                             "file_id": answer_response.file_id, "answers": answer_response.answers}

        return response_data
    except Exception as e:
        # Rollback and log other exceptions
        if db:
            db.rollback()
        print(f"An error occurred while updating user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

    finally:
        # Close the session
        if db:
            db.close()


def get_answer_from_gen_AI_without_auth(original_question: str, original_file_text: str):
    final_response = None
    try:
        final_answer = google_gen_AI_response(model_prompt=Config.GOOGLE_PROMPT, input_data_from_user=original_file_text,
                                              question=original_question)
        if final_answer:
            # save file in db
            updated_response = update_answer_in_table_without_auth(question_data=original_question,
                                                                   answer_data=final_answer)
            if updated_response:
                final_response = {"answers": updated_response["answers"], "qa_id": updated_response["question_id"], \
                                  "question": updated_response["question"]}
        return final_response

    except Exception as e:
        print(e)


def delete_file_using_file_id_without_auth(file_id: int):
    final_response = False
    try:
        db = next(get_db())

        # check file is present
        response = db.query(UserFilesData).filter(UserFilesData.file_id == file_id).first()
        if response:
            db.query(FileQuestions).filter(FileQuestions.file_id == file_id).delete()
            db.query(UserFilesData).filter(UserFilesData.file_id == file_id).delete()
            db.commit()
            final_response = True

        return final_response
    except Exception as e:
        # Rollback and log other exceptions
        if db:
            db.rollback()
        print(f"An error occurred while updating user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

    finally:
        # Close the session
        if db:
            db.close()
