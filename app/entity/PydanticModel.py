from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserFileUpload(BaseModel):
    title: str
    file: str
    user_id: int


class CreateQuestion(BaseModel):
    question: str


class Token(BaseModel):
    tokenId: str
