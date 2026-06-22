from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine
from app.models.models import Base
from app.routers import auth, notes, pdf, admin

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Notes Generator API",
    description="Full Stack AI-powered notes generator",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(notes.router)
app.include_router(pdf.router)
app.include_router(admin.router)

@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "AI Notes Generator API is running"
    }