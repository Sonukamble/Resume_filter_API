from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException
from passlib.context import CryptContext

from app.database.DatabaseConnection import get_db
from app.entity.PydanticModel import UserCreate
from app.entity.models import Users, UserFile, UserQuestions
from app.operation.JwtTokenCreation import verify_password, verify_password_reset_token

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_password_hash(password):
    return pwd_context.hash(password)


def create_user(user: UserCreate):
    try:
        # Manually retrieve the session from the generator
        db = next(get_db())

        hashed_password = get_password_hash(user.password)
        # Create a new user instance
        db_user = Users(username=user.username, email=user.email, hashed_password=hashed_password)

        # Add the user to the session and commit
        db.add(db_user)
        db.commit()

        # Refresh the instance to get updated data
        db.refresh(db_user)  # This line is fixed here

        return {"username": db_user.username, "email": db_user.email, "access_token": db_user.hashed_password}

    except HTTPException as http_ex:
        # Rollback and raise HTTP exceptions
        if db:
            db.rollback()
        print(f"An error occurred while creating user: {http_ex}")
        raise http_ex

    except Exception as e:
        # Rollback and log other exceptions
        if db:
            db.rollback()
        print(f"An error occurred while creating user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

    finally:
        if db:
            db.close()


def get_user_details(user_email: str, user_name: Optional[str] = None):
    response_data = None
    try:
        db = next(get_db())
        if user_name:
            user_details = db.query(Users).filter(
                (Users.username == user_name) | (Users.email == user_email)
            ).first()

            # if user_details and user_details.username == user_name:
            #     raise HTTPException(status_code=400, detail="Username already taken")
        else:
            user_details = db.query(Users).filter(Users.email == user_email).first()
            # if user_details and user_details.email == user_email:
            #     raise HTTPException(status_code=400, detail="Email already registered")
        if user_details:
            response_data = {"username": user_details.username, "email": user_details.email, "id": user_details.id,
                             "hashed_password": user_details.hashed_password}

        return response_data
    except Exception as e:
        db.rollback()
        print(e)
    finally:
        db.rollback()


def authenticate_user(email: str, password: str):
    try:
        # Manually retrieve the session from the generator
        db = next(get_db())

        user = db.query(Users).filter(Users.email == email).first()
        if not user or not verify_password(password, user.hashed_password):
            return False
        return user
    except Exception as e:
        db.rollback()
        print(e)
        raise
    finally:
        db.close()


def update_created_user(user_email: str, reset_token: str):
    try:
        # Manually retrieve the session from the generator
        db = next(get_db())
        # Query the user by email
        user = db.query(Users).filter(Users.email == user_email).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Update the reset token and expiration time
        user.reset_token = reset_token
        user.reset_token_expiration = datetime.utcnow() + timedelta(hours=1)

        # Commit the changes to the database
        db.commit()

        # Refresh the instance to get updated data (optional)
        db.refresh(user)

        return {"username": user.username, "email": user.email}

    except HTTPException as http_ex:
        # Rollback and raise HTTP exceptions
        if db:
            db.rollback()
        print(f"An error occurred while updating user: {http_ex}")
        raise http_ex

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


def verify_password_reset_token_and_get_email(access_toekn: str):
    try:
        verified_email = verify_password_reset_token(access_toekn)

        # Manually retrieve the session from the generator
        db = next(get_db())
        # Query the user by email
        user = db.query(Users).filter(Users.email == verified_email).first()

        return user
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


def save_file_in_db(filepath: str, host_ip: str, title: str, user: dict, pdf_text: str):
    response_data = None
    try:
        db = next(get_db())

        user_file = UserFile(title=title, file=filepath, user_id=user.id, host_ip=host_ip, resume_text=pdf_text)

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


def craete_question_entry(question: str, user_id: int, file_id: int):
    response_entry = None
    try:
        db = next(get_db())

        question_entry = UserQuestions(question=question, user_id=user_id, file_id=file_id)

        db.add(question_entry)
        db.commit()
        # Refresh the instance to get updated data
        db.refresh(question_entry)  # This line is fixed here
        if question_entry:
            response_entry = {"qa_id": question_entry.qa_id, "question": question_entry.question, \
                              "file_id": question_entry.file_id, "user_id": question_entry.user_id}
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


# def create_reset_token(user_id: int) -> str:
#     token = secrets.token_urlsafe()
#     expiration = datetime.utcnow() + timedelta(hours=1)  # Token valid for 1 hour
#
#     # Update the user with the reset token and expiration
#     db = next(get_db())
#     user = db.query(Users).filter(Users.id == user_id).first()
#     if user:
#         user.reset_token = token
#         user.reset_token_expiration = expiration
#         db.commit()
#
#     return token


#####
def get_file_details_from_user_id(user_id: int):
    file_details_response = None
    try:
        db = next(get_db())

        file_details = db.query(UserFile).filter(UserFile.user_id == user_id).first()

        if file_details:
            file_details_response = {"file_id": file_details.file_id, "title": file_details.title, \
                                     "file": file_details.file, "user_id": file_details.user_id, \
                                     "resume_text": file_details.resume_text, "host_ip": file_details.host_ip}
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


def update_answer_in_table(question_data: str, answer_data: str):
    response_data = None
    try:
        db = next(get_db())

        answer_response = db.query(UserQuestions).filter(UserQuestions.question == question_data).first()
        answer_response.answers = answer_data
        db.commit()
        db.refresh(answer_response)
        if answer_response:
            response_data = {"qa_id": answer_response.qa_id, "question": answer_response.question, \
                             "file_id": answer_response.file_id, "user_id": answer_response.user_id, \
                             "answers": answer_response.answers}

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


def get_chat_history_from_db(user_id: int):
    final_response_data = None
    try:
        db = next(get_db())

        response_list = db.query(UserQuestions).filter(UserQuestions.user_id == user_id).all()
        print(response_list)
        if response_list:
            final_response_data = [
                {
                    "qa_id": question.qa_id,
                    "question": question.question,
                    "answers": question.answers,
                    "file_id": question.file_id,
                    "user_id": question.user_id
                }
                for question in response_list
            ]
        return final_response_data
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


def get_chat_history_using_file_id(file_id: int):
    final_response_data = None
    try:
        db = next(get_db())

        response_list = db.query(UserQuestions).filter(UserQuestions.file_id == file_id).all()
        print(response_list)
        if response_list:
            final_response_data = [
                {
                    "qa_id": question.qa_id,
                    "question": question.question,
                    "answers": question.answers,
                    "file_id": question.file_id,
                    "user_id": question.user_id
                }
                for question in response_list
            ]
        return final_response_data
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


def delete_chat_data(qa_id: list[int]):
    response = None
    try:
        db = next(get_db())

        existing_data = db.query(UserQuestions).filter(UserQuestions.qa_id.in_(qa_id)).all()
        extracting_ids = [question.qa_id for question in existing_data]

        if extracting_ids:
            db.query(UserQuestions).filter(UserQuestions.qa_id.in_(extracting_ids)).delete(synchronize_session=False)
            db.commit()
            response = extracting_ids

        return response
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


def delete_file_using_file_id(file_id: int):
    final_response = False
    try:
        db = next(get_db())

        # check file is present
        response = db.query(UserFile).filter(UserFile.file_id == file_id).first()
        if response:
            db.query(UserQuestions).filter(UserQuestions.file_id == file_id).delete()
            db.query(UserFile).filter(UserFile.file_id == file_id).delete()
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
