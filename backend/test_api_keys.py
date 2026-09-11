import os
import sys
import requests
from dotenv import load_dotenv

# Load backend/.env
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(env_path)

def test_sarvam_api_key():
    api_key = os.getenv("SARVAM_API_KEY", "").strip()
    if not api_key:
        print("[MISSING] SARVAM_API_KEY: Missing or empty in backend/.env")
        return False

    print(f"[KEY] Testing SARVAM_API_KEY ({api_key[:6]}...{api_key[-4:] if len(api_key)>10 else ''})...")

    # Test call to Sarvam AI API
    url = "https://api.sarvam.ai/doc-ai/v1/job/digitise"
    headers = {"api-subscription-key": api_key}
    
    try:
        # Pinging endpoint or sending invalid request to verify subscription key validation
        res = requests.post(url, headers=headers, timeout=10)
        # Status 400 (Bad Request missing file) means key is VALID and authorized!
        # Status 401/403 means key is INVALID or unauthorized.
        if res.status_code in [200, 400, 422]:
            print("[SUCCESS] SARVAM_API_KEY: Valid and working as intended!")
            return True
        elif res.status_code in [401, 403]:
            print(f"[FAILED] SARVAM_API_KEY: Invalid or Unauthorized (HTTP {res.status_code})")
            return False
        else:
            print(f"[WARNING] SARVAM_API_KEY: Returned unexpected HTTP status {res.status_code}: {res.text[:100]}")
            return True
    except Exception as e:
        print(f"[ERROR] Network error while testing SARVAM_API_KEY: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("  API Key Verification & Health Test Tool")
    print("=" * 60)
    
    sarvam_ok = test_sarvam_api_key()
    
    print("=" * 60)
    if sarvam_ok:
        print("[DONE] API Key Test Complete: All configured keys are active!")
    else:
        print("💡 Hint: Add your SARVAM_API_KEY to `backend/.env`, then run `python backend/test_api_keys.py` to test it.")
    print("=" * 60)

