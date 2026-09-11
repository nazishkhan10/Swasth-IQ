import os
import io
import fitz # PyMuPDF
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def _register_and_login() -> str:
    email = f"ocr_user_{uuid.uuid4().hex[:8]}@example.com"
    client.post(
        "/api/v1/auth/register",
        json={"name": "OCR User", "email": email, "password": "Password123!", "confirm_password": "Password123!"}
    )
    res = client.post("/api/v1/auth/login", json={"email": email, "password": "Password123!"})
    return res.json()["access_token"]


def get_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}



def test_ocr_txt_file_flow():
    headers = get_headers(_register_and_login())
    # 1. Upload sample text report
    txt_content = "PATIENT REPORT\nName: John Doe\n\nHEMOGLOBIN: 14.5 g/dL (Ref: 13.0 - 17.0)\nWBC COUNT: 6.8 10^3/uL\n"
    files = {"file": ("cbc_report.txt", io.BytesIO(txt_content.encode("utf-8")), "text/plain")}
    upload_res = client.post("/api/v1/upload", files=files, headers=headers)
    assert upload_res.status_code == 201
    report_id = upload_res.json()["id"]

    # 2. Run OCR
    ocr_res = client.post(f"/api/v1/ocr/{report_id}", headers=headers)
    assert ocr_res.status_code == 200
    data = ocr_res.json()
    assert data["status"] == "completed"
    assert data["engine"] == "PlainText"
    assert data["confidence"] == 1.0
    assert len(data["pages"]) == 1
    assert "PATIENT REPORT" in data["pages"][0]["text"]

    # 3. Test caching behavior
    cache_res = client.post(f"/api/v1/ocr/{report_id}", headers=headers)
    assert cache_res.status_code == 200
    assert cache_res.json()["version"] == 1

    # 4. Test force retry & versioning
    retry_res = client.post(f"/api/v1/ocr/{report_id}/retry?engine=PlainText", headers=headers)
    assert retry_res.status_code == 200
    assert retry_res.json()["version"] == 2

    # 5. Fetch OCR blocks endpoint
    blocks_res = client.get(f"/api/v1/ocr/{report_id}/blocks", headers=headers)
    assert blocks_res.status_code == 200
    b_data = blocks_res.json()
    assert b_data["total_blocks"] > 0
    assert b_data["version"] == 2


def test_ocr_pdf_file_flow():
    headers = get_headers(_register_and_login())
    # Create sample Digital PDF in-memory using PyMuPDF
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "COMPLETE BLOOD COUNT REPORT", fontsize=16)
    page.insert_text((50, 100), "Hemoglobin: 13.8 g/dL (Normal)", fontsize=12)
    pdf_bytes = doc.tobytes()
    doc.close()

    # Upload PDF
    files = {"file": ("digital_cbc.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
    upload_res = client.post("/api/v1/upload", files=files, headers=headers)
    assert upload_res.status_code == 201
    report_id = upload_res.json()["id"]

    # Run OCR
    ocr_res = client.post(f"/api/v1/ocr/{report_id}", headers=headers)
    assert ocr_res.status_code == 200
    data = ocr_res.json()
    assert data["status"] == "completed"
    assert any(eng in data["engine"] for eng in ["PyMuPDF", "Sarvam Document Intelligence"])
    assert data["confidence"] >= 0.8
    assert len(data["pages"]) == 1
    assert "COMPLETE BLOOD COUNT REPORT" in data["pages"][0]["text"]

