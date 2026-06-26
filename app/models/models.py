from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime

class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.user, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    notes = relationship("Note", back_populates="owner", cascade="all, delete")


class Note(Base):
    __tablename__ = "notes"

    note_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    topic = Column(String(150), nullable=False)
    generated_note = Column(Text, nullable=False)
    word_limit = Column(Integer, nullable=True)
    language = Column(String(50), default="English")
    source = Column(String(50), default="topic")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="notes")
    class PDFDocument(Base):
        __tablename__ = "pdf_documents"

        pdf_id = Column(Integer, primary_key=True, index=True)
        user_id = Column(Integer, ForeignKey("users.user_id"))
        filename = Column(String(255))
        extracted_text = Column(Text)
        summary = Column(Text, nullable=True)
        created_at = Column(DateTime, default=datetime.utcnow)