from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
import PyPDF2
import io

from app.database import get_db
from app.models.models import Note, User
from app.schemas.schemas import NoteOut
from app.utils.auth import get_current_user
from app.utils.gemini import summarize_pdf_text

router = APIRouter(prefix="/pdf", tags=["PDF"])


@router.post("/upload", response_model=NoteOut, status_code=201)
async def upload_pdf(
    file: UploadFile = File(...),
    language: str = Form("English"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB")

    try:
        reader = PyPDF2.PdfReader(io.BytesIO(contents))
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read PDF. Make sure it's a valid file")

    if not text.strip():
        raise HTTPException(status_code=400, detail="No readable text found in the PDF")

    summary = summarize_pdf_text(text, language)

    topic = file.filename.replace(".pdf", "").replace("_", " ").title()
    note = Note(
        user_id=current_user.user_id,
        topic=topic,
        generated_note=summary,
        word_limit=None,
        language=language,
        source="pdf",
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note