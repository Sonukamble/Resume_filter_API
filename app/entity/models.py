from sqlalchemy import Column, Integer, String, DateTime, TEXT

from app.database.DatabaseConnection import Base


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    reset_token = Column(String(255), nullable=True)
    reset_token_expiration = Column(DateTime, nullable=True)
    google_id = Column(String(255), unique=True, nullable=True)


class UserFile(Base):
    __tablename__ = 'user_files'

    file_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    file = Column(String(255), nullable=False)
    user_id = Column(Integer, nullable=False)
    host_ip = Column(String(45), nullable=True)
    resume_text = Column(TEXT, nullable=True)


class UserQuestions(Base):
    __tablename__ = 'user_questions'

    qa_id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    question = Column(String(255), nullable=False)
    answers = Column(TEXT)
    file_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
