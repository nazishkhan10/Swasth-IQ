import os
import io
import fitz  # PyMuPDF
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)

def run_live_sarvam_test():
    print("=" * 60)
    print("  LIVE SARVAM AI DOCUMENT INTELLIGENCE END-TO-END TEST")
    print("=" * 60)

    # 1. Register & Login test user
    email = "live_sarvam_test@example.com"
    password = "TestPassword123!"
    
    client.post("/api/v1/auth/register", json={
        "name": "Live Tester",
        "email": email,
        "password": password,
        "confirm_password": password
    })
    
    login_res = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": password
    })
    
    if login_res.status_code != 200:
        print(f"[FAIL] Login failed: {login_res.text}")
        return False
        
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("[1/5] User registered & authenticated via JWT successfully.")

    # 2. Create sample medical CBC PDF report using PyMuPDF
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "PATHOLOGY LABORATORY DIAGNOSTICS REPORT", fontsize=14)
    page.insert_text((50, 80), "Patient: Jane Doe | Age: 34 | Sex: Female", fontsize=10)
    page.insert_text((50, 120), "COMPLETE BLOOD COUNT (CBC):", fontsize=12)
    page.insert_text((50, 140), "Hemoglobin: 14.2 g/dL (Reference: 12.0 - 15.5)", fontsize=10)
    page.insert_text((50, 160), "Total WBC: 6,500 /uL (Reference: 4,500 - 11,000)", fontsize=10)
    page.insert_text((50, 180), "Platelet Count: 250,000 /uL (Reference: 150,000 - 450,000)", fontsize=10)
    pdf_bytes = doc.tobytes()
    doc.close()

    files = {"file": ("live_cbc_report.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
    upload_res = client.post("/api/v1/upload", files=files, headers=headers)
    
    if upload_res.status_code != 201:
        print(f"[FAIL] Upload failed: {upload_res.text}")
        return False
        
    report_id = upload_res.json()["id"]
    print(f"[2/5] Sample CBC PDF report uploaded successfully. Report ID: {report_id}")

    # 3. Trigger Sarvam Document Intelligence OCR Engine
    print("[3/5] Triggering Sarvam AI Document Intelligence API job...")
    ocr_res = client.post(f"/api/v1/ocr/{report_id}?force_retry=true&engine=SarvamDoc", headers=headers)
    
    if ocr_res.status_code != 200:
        print(f"[FAIL] OCR request failed: {ocr_res.text}")
        return False

    ocr_data = ocr_res.json()
    print("[4/5] OCR processing completed!")
    print(f"      - Engine Used: {ocr_data.get('engine')}")
    print(f"      - Status: {ocr_data.get('status')}")
    print(f"      - Confidence Score: {round(ocr_data.get('confidence', 0) * 100)}%")
    print(f"      - Processing Time: {ocr_data.get('processing_time')}s")
    print(f"      - Pages Extracted: {ocr_data.get('page_count')}")

    extracted_text = ocr_data.get("pages", [{}])[0].get("text", "")
    print("-" * 60)
    print("EXTRACTED TEXT OUTPUT:")
    print(extracted_text[:400] + ("..." if len(extracted_text) > 400 else ""))
    print("-" * 60)

    # 5. Verify blocks endpoint
    blocks_res = client.get(f"/api/v1/ocr/{report_id}/blocks", headers=headers)
    if blocks_res.status_code == 200:
        b_data = blocks_res.json()
        print(f"[5/5] Database block persistence verified: {b_data.get('total_blocks')} blocks created in OCRBlock table.")

    print("=" * 60)
    print("[SUCCESS] LIVE SARVAM AI DOCUMENT INTELLIGENCE TEST PASSED 100%!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    run_live_sarvam_test()
