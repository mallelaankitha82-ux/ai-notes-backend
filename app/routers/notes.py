from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse, PlainTextResponse
from sqlalchemy.orm import Session
import io

from app.database import get_db
from app.models.models import Note, User
from app.schemas.schemas import NoteGenerateRequest, NoteOut, NoteListOut
from app.utils.auth import get_current_user
from app.utils.gemini import generate_notes

router = APIRouter(prefix="/notes", tags=["Notes"])


@router.post("/generate", response_model=NoteOut, status_code=201)
def generate(
    payload: NoteGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    content = generate_notes(
        payload.topic,
        payload.word_limit,
        payload.language
    )

    note = Note(
        user_id=current_user.user_id,
        topic=payload.topic,
        generated_note=content,
        word_limit=payload.word_limit,
        language=payload.language,
        source="topic",
    )

    db.add(note)
    db.commit()
    db.refresh(note)

    return note


@router.get("", response_model=NoteListOut)
def get_all_notes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == "admin":
        notes = db.query(Note).order_by(Note.created_at.desc()).all()
    else:
        notes = (
            db.query(Note)
            .filter(Note.user_id == current_user.user_id)
            .order_by(Note.created_at.desc())
            .all()
        )

    return NoteListOut(notes=notes, total=len(notes))


@router.get("/search", response_model=NoteListOut)
def search_notes(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notes = (
        db.query(Note)
        .filter(
            Note.user_id == current_user.user_id,
            Note.topic.ilike(f"%{q}%") |
            Note.generated_note.ilike(f"%{q}%"),
        )
        .order_by(Note.created_at.desc())
        .all()
    )

    return NoteListOut(notes=notes, total=len(notes))


@router.get("/download/{note_id}")
def download_note(
    note_id: int,
    format: str = Query("txt"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = db.query(Note).filter(Note.note_id == note_id).first()

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    if note.user_id != current_user.user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    if format == "txt":
        content = (
            f"Topic: {note.topic}\n"
            f"Language: {note.language}\n\n"
            f"{note.generated_note}"
        )

        return PlainTextResponse(
            content=content,
            headers={
                "Content-Disposition":
                f'attachment; filename="note_{note_id}.txt"'
            },
        )

    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, f"Topic: {note.topic}")

    pdf.ln(10)

    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 7, note.generated_note)

    pdf_data = pdf.output(dest="S")

    if isinstance(pdf_data, str):
        pdf_data = pdf_data.encode("latin-1")

    return StreamingResponse(
        io.BytesIO(pdf_data),
        media_type="application/pdf",
        headers={
            "Content-Disposition":
            f'attachment; filename="note_{note_id}.pdf"'
        },
    )


@router.delete("/{note_id}")
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = db.query(Note).filter(Note.note_id == note_id).first()

    if not note:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    if (
        note.user_id != current_user.user_id
        and current_user.role != "admin"
    ):
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    db.delete(note)
    db.commit()

    return {
        "message": "Note deleted successfully"
    }