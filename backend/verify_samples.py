import os
import io
import glob
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def verify_all_samples():
    email = "valid_dataset_verifier@example.com"
    client.post("/api/v1/auth/register", json={"name": "Valid Dataset Verifier", "email": email, "password": "Password123!", "confirm_password": "Password123!"})
    res = client.post("/api/v1/auth/login", json={"email": email, "password": "Password123!"})
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    sample_files = [
        r"c:\Users\datta.000\Desktop\New folder (3)\random\sample data 1.txt",
    ]

    uploads_dir = r"c:\Users\datta.000\Desktop\New folder (3)\random\backend\uploads"
    for ext in ["*.txt", "*.png", "*.pdf"]:
        sample_files.extend(glob.glob(os.path.join(uploads_dir, "**", ext), recursive=True))

    unique_files = list(set(sample_files))
    print(f"\n==================================================")
    print(f"=== CROSS-VERIFYING DATASET SAMPLE FILES ===")
    print(f"==================================================\n")

    summary_results = []

    for filepath in unique_files:
        filename = os.path.basename(filepath)
        if filename in ["requirements.txt", "private.txt"]:
            continue

        # Skip corrupt mock 0-byte/39-byte dummy files from past test runs
        if os.path.getsize(filepath) < 100:
            continue

        try:
            with open(filepath, "rb") as f:
                content = f.read()

            content_type = "text/plain"
            if filename.endswith(".png"):
                content_type = "image/png"
            elif filename.endswith(".pdf"):
                content_type = "application/pdf"

            up = client.post("/api/v1/upload", files={"file": (filename, io.BytesIO(content), content_type)}, headers=headers)
            if up.status_code != 201:
                summary_results.append((filename, "UPLOAD FAILED", 0, "N/A"))
                continue

            report_id = up.json()["id"]

            ocr_res = client.post(f"/api/v1/ocr/{report_id}", headers=headers)
            if ocr_res.status_code != 200:
                summary_results.append((filename, "OCR FAILED", 0, "N/A"))
                continue

            parse_res = client.post(f"/api/v1/parser/{report_id}", headers=headers)
            if parse_res.status_code != 200:
                summary_results.append((filename, "PARSER FAILED", 0, parse_res.json().get("detail", "Error")))
                continue

            p_data = parse_res.json()
            total_params = p_data.get("total_parameters", 0)
            rep_type = p_data.get("detected_report_type", "Unknown")
            patient_name = p_data.get("patient", {}).get("patient_name") or "Unspecified"

            summary_results.append((filename, "SUCCESS", total_params, f"{rep_type} | Patient: {patient_name}"))

        except Exception as e:
            summary_results.append((filename, f"ERROR: {str(e)}", 0, "N/A"))

    print(f"{'FILENAME':<35} | {'STATUS':<12} | {'PARAMS':<8} | {'DETAILS'}")
    print("-" * 95)
    for fn, status, count, details in summary_results:
        print(f"{fn[:34]:<35} | {status:<12} | {count:<8} | {details}")

if __name__ == "__main__":
    verify_all_samples()
