import os
import sys
import io
import uuid
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# ─── Helpers ──────────────────────────────────────────────────────────────────
def _register_and_login() -> str:
    """Register a unique user and return JWT token."""
    email = f"upload_test_{uuid.uuid4().hex[:8]}@example.com"
    client.post(
        "/api/v1/auth/register",
        json={"name": "Test User", "email": email, "password": "test1234", "confirm_password": "test1234"},
    )
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": "test1234"})
    return resp.json()["access_token"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ─── Health Check ─────────────────────────────────────────────────────────────
def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


# ─── Upload Tests ─────────────────────────────────────────────────────────────
def test_upload_txt_success():
    token = _register_and_login()
    content = b"Haemoglobin: 14.2 g/dL\nWBC: 7800 cells/mcL\nPlatelet: 250000/mcL"
    r = client.post(
        "/api/v1/upload",
        headers=auth_headers(token),
        files={"file": ("blood_report.txt", io.BytesIO(content), "text/plain")},
        data={"upload_source": "upload"},
    )
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["original_filename"] == "blood_report.txt"
    assert data["status"] == "uploaded"
    assert data["file_url"] is not None


def test_upload_pdf_success():
    token = _register_and_login()
    # Minimal valid PDF header bytes
    content = b"%PDF-1.4 1 0 obj<</Type/Catalog>>endobj"
    r = client.post(
        "/api/v1/upload",
        headers=auth_headers(token),
        files={"file": ("report.pdf", io.BytesIO(content), "application/pdf")},
        data={"upload_source": "upload"},
    )
    assert r.status_code == 201, r.text
    assert r.json()["mime_type"] == "application/pdf"


def test_upload_requires_auth():
    content = b"some text"
    r = client.post(
        "/api/v1/upload",
        files={"file": ("report.txt", io.BytesIO(content), "text/plain")},
    )
    assert r.status_code == 401


def test_upload_rejects_unsupported_extension():
    token = _register_and_login()
    r = client.post(
        "/api/v1/upload",
        headers=auth_headers(token),
        files={"file": ("script.exe", io.BytesIO(b"MZ"), "application/octet-stream")},
    )
    assert r.status_code == 400
    assert "not supported" in r.json()["detail"].lower()


def test_upload_rejects_empty_file():
    token = _register_and_login()
    r = client.post(
        "/api/v1/upload",
        headers=auth_headers(token),
        files={"file": ("empty.txt", io.BytesIO(b""), "text/plain")},
    )
    assert r.status_code == 400


# ─── Files List & Delete ──────────────────────────────────────────────────────
def test_list_and_delete_report():
    token = _register_and_login()
    content = b"Test medical report content"

    # Upload
    r = client.post(
        "/api/v1/upload",
        headers=auth_headers(token),
        files={"file": ("test.txt", io.BytesIO(content), "text/plain")},
        data={"upload_source": "upload"},
    )
    assert r.status_code == 201
    report_id = r.json()["id"]

    # List — should contain our upload
    r = client.get("/api/v1/files", headers=auth_headers(token))
    assert r.status_code == 200
    ids = [item["id"] for item in r.json()]
    assert report_id in ids

    # Delete
    r = client.delete(f"/api/v1/files/{report_id}", headers=auth_headers(token))
    assert r.status_code == 204

    # List again — should not contain deleted
    r = client.get("/api/v1/files", headers=auth_headers(token))
    ids_after = [item["id"] for item in r.json()]
    assert report_id not in ids_after


def test_delete_other_users_file_is_404():
    token_a = _register_and_login()
    token_b = _register_and_login()

    # User A uploads
    r = client.post(
        "/api/v1/upload",
        headers=auth_headers(token_a),
        files={"file": ("private.txt", io.BytesIO(b"private"), "text/plain")},
    )
    report_id = r.json()["id"]

    # User B tries to delete User A's file
    r = client.delete(f"/api/v1/files/{report_id}", headers=auth_headers(token_b))
    assert r.status_code == 404


def test_stats_endpoint():
    token = _register_and_login()
    content = b"CBC Report data"
    client.post(
        "/api/v1/upload",
        headers=auth_headers(token),
        files={"file": ("cbc.txt", io.BytesIO(content), "text/plain")},
    )
    r = client.get("/api/v1/files/stats", headers=auth_headers(token))
    assert r.status_code == 200
    data = r.json()
    assert data["total_reports"] >= 1
    assert data["total_size_bytes"] > 0
