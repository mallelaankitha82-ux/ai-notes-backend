from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
import PyPDF2
import io

from app.database import get_db
from app.models.models import Note, User
from app.schemas.schemas import NoteOut
from app.utils.auth import get_current_user
from app.utils.gemini import summarize_text, ask_pdf_question

router = APIRouter(
    prefix="/pdf",
    tags=["PDF"]
)


class AskPDFRequest(BaseModel):
    pdf_text: str
    question: str


@router.post("/ask")
def ask_question(
    payload: AskPDFRequest,
    current_user: User = Depends(get_current_user),
):
    answer = ask_pdf_question(
        payload.pdf_text,
        payload.question,
    )

    return {
        "question": payload.question,
        "answer": answer,
    }


@router.post("/upload", response_model=NoteOut, status_code=201)
async def upload_pdf(
    file: UploadFile = File(...),
    language: str = Form("English"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    # Validate extension
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are accepted"
        )

    contents = await file.read()

    # Max 10 MB
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="Maximum file size is 10 MB"
        )

    # Read PDF
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(contents))

        text = ""

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    except Exception as e:
        print("PDF Read Error:", repr(e))

        raise HTTPException(
            status_code=400,
            detail=f"Unable to read PDF: {str(e)}"
        )

    if not text.strip():
        raise HTTPException(
            status_code=400,
            detail="No readable text found in PDF"
        )

    print("PDF Text Length:", len(text))

    # Gemini token limit avoid cheyyadaniki
    if len(text) > 20000:
        text = text[:20000]

    try:
        summary = summarize_text(text)

        print("Summary generated successfully")

    except Exception as e:

        print("Gemini Summary Error:", repr(e))

        raise HTTPException(
            status_code=500,
            detail=f"Gemini Error: {str(e)}"
        )

    topic = (
        file.filename
        .replace(".pdf", "")
        .replace("_", " ")
        .title()
    )

    note = Note(
        user_id=current_user.user_id,
        topic=topic,
        generated_note=summary,
        word_limit=300,
        language=language,
        source="pdf",
    )

    db.add(note)
    db.commit()
    db.refresh(note)

    return note