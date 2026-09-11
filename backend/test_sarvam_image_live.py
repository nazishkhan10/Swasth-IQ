import io
import fitz
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_live_sarvam_vision():
    print("=" * 60)
    print("  LIVE SARVAM VISION OCR END-TO-END TEST")
    print("=" * 60)

    # 1. Login user
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
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Render medical report scan image
    doc = fitz.open()
    page = doc.new_page(width=600, height=250)
    page.insert_text((50, 40), "METRO GENERAL HOSPITAL DIAGNOSTICS", fontsize=14)
    page.insert_text((50, 80), "COMPREHENSIVE METABOLIC & LIPID PANEL", fontsize=12)
    page.insert_text((50, 120), "Serum Fasting Glucose: 110 mg/dL (High)", fontsize=10)
    page.insert_text((50, 150), "Total Cholesterol: 215 mg/dL (High)", fontsize=10)
    page.insert_text((50, 180), "Triglycerides: 165 mg/dL (Borderline)", fontsize=10)
    pix = page.get_pixmap(dpi=150)
    png_bytes = pix.tobytes("png")
    doc.close()

    # 3. Upload PNG image report
    files = {"file": ("metabolic_panel_scan.png", io.BytesIO(png_bytes), "image/png")}
    upload_res = client.post("/api/v1/upload", files=files, headers=headers)
    assert upload_res.status_code == 201
    report_id = upload_res.json()["id"]
    print(f"[1/3] Uploaded medical scan PNG image (Report #{report_id})")

    # 4. Trigger Sarvam Vision OCR Engine
    print(f"[2/3] Triggering Sarvam Vision OCR for Report #{report_id}...")
    ocr_res = client.post(f"/api/v1/ocr/{report_id}?force_retry=true", headers=headers)
    assert ocr_res.status_code == 200
    ocr_data = ocr_res.json()

    print("[3/3] Sarvam Vision OCR processing complete!")
    print(f"      - Engine: {ocr_data.get('engine')}")
    print(f"      - Document Type: {ocr_data.get('document_type')}")
    print(f"      - Processing Time: {ocr_data.get('processing_time')}s")
    
    ext_text = ocr_data.get("pages", [{}])[0].get("text", "")
    print("-" * 60)
    print("EXTRACTED IMAGE OCR TEXT:")
    print(ext_text)
    print("-" * 60)
    
    assert "Sarvam Vision OCR" in ocr_data.get("engine")
    assert "METRO GENERAL HOSPITAL" in ext_text or "Serum Fasting Glucose" in ext_text or "Cholesterol" in ext_text
    print("[SUCCESS] LIVE SARVAM VISION OCR TEST PASSED 100%!")

if __name__ == "__main__":
    test_live_sarvam_vision()
