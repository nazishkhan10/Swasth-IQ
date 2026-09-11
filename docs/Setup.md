# Developer Setup Guide

## Prerequisites
- Python 3.10+
- Node.js 18+ & npm
- Git

## 1. Backend Setup

```bash
cd backend
python -m venv venv
# Activate virtual environment
# Windows: venv\Scripts\activate
# Linux/macOS: source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

Configure `.env` with:
```env
OPENAI_API_KEY=your_openai_key
DATABASE_URL=sqlite:///./sql_app.db
SECRET_KEY=your_secret_key
JWT_SECRET=your_jwt_secret
```

Run FastAPI Backend:
```bash
python run.py
```
Backend runs at `http://localhost:8000`.

## 2. Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env
```

Configure `.env`:
```env
VITE_API_BASE_URL=http://localhost:8000
```

Run Frontend Development Server:
```bash
npm run dev
```
Frontend runs at `http://localhost:5173`.
