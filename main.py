import pytesseract

# Set tesseract path (change if different in your PC)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# main.py  -- prescription OCR -> save to SQLite
import os
import cv2
import pytesseract
import sqlite3
import numpy as np

# If tesseract is not found on PATH, uncomment and set the correct path:
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

DB_FILE = "prescriptions.db"

# ---------------- image preprocessing ----------------
def deskew(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bitwise_not(gray)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    coords = np.column_stack(np.where(thresh > 0))
    if coords.size == 0:
        return image
    rect = cv2.minAreaRect(coords)
    angle = rect[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = image.shape[:2]
    M = cv2.getRotationMatrix2D((w//2, h//2), angle, 1.0)
    return cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

def preprocess(image_path):
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Cannot open image: {image_path}")
    img = deskew(img)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # CLAHE (contrast)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    gray = clahe.apply(gray)
    # Denoise
    gray = cv2.fastNlMeansDenoising(gray, h=10)
    # Adaptive threshold
    th = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                cv2.THRESH_BINARY,31,15)
    return th

# ---------------- OCR ----------------
def do_ocr(image_path):
    img = preprocess(image_path)
    # Tesseract expects either path or numpy array; use image_to_string
    # Use config: OEM 1 (LSTM), PSM 6 (Assume a block of text)
    config = "--oem 1 --psm 6"
    text = pytesseract.image_to_string(img, config=config, lang='eng')
    return text.strip()

# ---------------- Database ----------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS prescriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        extracted_text TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

def save_record(filename, text):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("INSERT INTO prescriptions (filename, extracted_text) VALUES (?, ?)", (filename, text))
    conn.commit()
    conn.close()

def show_all():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT id, filename, created_at FROM prescriptions ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

# ---------------- Main CLI ----------------
if __name__ == "__main__":
    print("=== Prescription OCR -> SQLite (simple) ===")
    init_db()
    img_path = input("Enter path to prescription image (e.g. data/samples/rx1.jpg): ").strip()
    if not os.path.exists(img_path):
        print("File not found:", img_path)
        raise SystemExit(1)
    try:
        extracted = do_ocr(img_path)
    except Exception as e:
        print("Error during OCR:", e)
        raise

    print("\n--- Extracted Text ---\n")
    print(extracted if extracted else "[NO TEXT FOUND]")
    save_record(os.path.basename(img_path), extracted)
    print("\nSaved to database:", DB_FILE)
    print("\nRecent records:")
    for r in show_all()[:10]:
        print(r)
