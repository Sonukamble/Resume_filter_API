from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, TEXT, TIMESTAMP
from sqlalchemy.sql import func

from app.without_auth_router.file_entity.DBConnection import Base


class UserFilesData(Base):
    __tablename__ = 'files_data'

    file_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    file = Column(String(255), nullable=False)
    host_ip = Column(String(45), nullable=True)
    resume_text = Column(TEXT, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)


class FileQuestions(Base):
    __tablename__ = 'file_questions'

    question_id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    question = Column(String(255), nullable=False)
    answers = Column(TEXT)
    file_id = Column(Integer, nullable=False)


class QuestionBase(BaseModel):
    file_id: int
    question: str
