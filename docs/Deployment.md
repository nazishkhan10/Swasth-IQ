# Deployment & Production Guide

## Production Architecture

### Backend Deployment (Uvicorn / Gunicorn)
- Serve FastAPI via Uvicorn behind Nginx reverse proxy.
- Set environment variables (`OPENAI_API_KEY`, `JWT_SECRET`, `CORS_ORIGINS`).

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend Deployment (Static Hosting / Vercel / Nginx)
- Build optimized production bundle:

```bash
cd frontend
npm run build
```
- Serve static contents of `frontend/dist/`.
