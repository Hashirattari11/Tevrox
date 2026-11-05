@echo off
cd /d D:\tevrox\Tevrox\backend
call .venv\Scripts\activate
set DATABASE_URL=sqlite:///./tevrox.db
uvicorn app.main:app --host 0.0.0.0 --port 8010 --reload