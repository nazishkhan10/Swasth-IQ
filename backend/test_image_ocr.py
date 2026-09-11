import os
import fitz
from PIL import Image
from app.services.ocr.sarvam_doc_engine import SarvamDocEngine
from app.services.ocr.sarvam_vision_engine import SarvamVisionEngine
from app.services.ocr.tesseract_engine import TesseractEngine

def test_image_ocr():
    print("=" * 60)
    print("  TESTING IMAGE OCR ENGINES")
    print("=" * 60)

    # Find an image file in uploads or create a sample PNG
    img_path = os.path.join(os.path.dirname(__file__), "test_image.png")
    img = Image.new('RGB', (600, 200), color=(255, 255, 255))
    doc_fitz = fitz.open()
    page = doc_fitz.new_page(width=600, height=200)
    page.insert_text((50, 50), "TEST BLOOD REPORT IMAGE", fontsize=16)
    page.insert_text((50, 100), "Glucose: 95 mg/dL (Reference: 70 - 99)", fontsize=12)
    pix = page.get_pixmap()
    pix.save(img_path)
    doc_fitz.close()

    print(f"Created test image at: {img_path}")

    # 1. Test Sarvam Doc Engine on image
    print("\n[1] Testing SarvamDocEngine on image...")
    sarvam_doc = SarvamDocEngine()
    res1 = sarvam_doc.extract(img_path)
    print(f"Result Engine: {res1.get('engine')}")
    print(f"Extracted Text: {res1.get('pages', [{}])[0].get('text', '')[:200]}")

    # 2. Test Tesseract Fallback Engine on image
    print("\n[2] Testing TesseractEngine on image...")
    tess = TesseractEngine()
    res2 = tess.extract(img_path)
    print(f"Result Engine: {res2.get('engine')}")
    print(f"Extracted Text: {res2.get('pages', [{}])[0].get('text', '')[:200]}")

    if os.path.exists(img_path):
        os.remove(img_path)

if __name__ == "__main__":
    test_image_ocr()
