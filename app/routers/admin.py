from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import User, Note
from app.schemas.schemas import UserOut, NoteOut, AdminStats
from app.utils.auth import get_admin_user

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats", response_model=AdminStats)
def get_stats(
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user)
):
    total_users = db.query(User).filter(User.role == "user").count()
    total_notes = db.query(Note).count()
    total_pdf_notes = db.query(Note).filter(Note.source == "pdf").count()

    return AdminStats(
        total_users=total_users,
        total_notes=total_notes,
        total_pdf_notes=total_pdf_notes,
    )


@router.get("/users", response_model=list[UserOut])
def get_all_users(
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user)
):
    return db.query(User).order_by(User.created_at.desc()).all()


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user)
):
    user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role == "admin":
        raise HTTPException(
            status_code=400,
            detail="Cannot delete admin accounts"
        )

    db.delete(user)
    db.commit()

    return {"message": f"User {user_id} deleted successfully"}


@router.get("/notes", response_model=list[NoteOut])
def get_all_notes(
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user)
):
    return db.query(Note).order_by(Note.created_at.desc()).all()