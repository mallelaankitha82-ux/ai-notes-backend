echo from fastapi import FastAPI > main.py
echo from fastapi.middleware.cors import CORSMiddleware >> main.py
echo from app.database import engine >> main.py
echo from app.models.models import Base >> main.py
echo from app.routers import auth, notes, pdf, admin >> main.py
echo Base.metadata.create_all(bind=engine) >> main.py
echo app = FastAPI(title="AI Notes Generator API", description="Full Stack AI-powered notes generator", version="1.0.0") >> main.py
echo app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "https://your-frontend.vercel.app"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]) >> main.py
echo app.include_router(auth.router) >> main.py
echo app.include_router(notes.router) >> main.py
echo app.include_router(pdf.router) >> main.py
echo app.include_router(admin.router) >> main.py
echo @app.get("/") >> main.py
echo def root(): >> main.py
echo     return {"status": "ok", "message": "AI Notes Generator API is running"} >> main.py