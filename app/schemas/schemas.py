from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models.models import UserRole
from pydantic import BaseModel

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    name: str


class UserOut(BaseModel):
    user_id: int
    name: str
    email: str
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True


class NoteGenerateRequest(BaseModel):
    topic: str
    word_limit: Optional[int] = 300
    language: Optional[str] = "English"


class NoteOut(BaseModel):
    note_id: int
    user_id: int
    topic: str
    generated_note: str
    word_limit: Optional[int]
    language: str
    source: str
    created_at: datetime

    class Config:
        from_attributes = True


class NoteListOut(BaseModel):
    notes: list[NoteOut]
    total: int


class PDFSummaryOut(BaseModel):
    note_id: int
    topic: str
    generated_note: str
    created_at: datetime

    class Config:
        from_attributes = True


class AdminStats(BaseModel):
    total_users: int
    total_notes: int
    total_pdf_notes: int
class PDFOut(BaseModel):
    pdf_id: int
    filename: str

class Config:
        from_attributes = True