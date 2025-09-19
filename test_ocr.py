import cv2
import pytesseract
from PIL import Image

# Set tesseract path (update if needed)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Path to image
image_path = r"C:\Users\User\my_prescription_ocr\data\samples\rx1.jpg.jpg"

# ✅ Method 1: Directly give file path to pytesseract
text = pytesseract.image_to_string(Image.open(image_path))

print("📝 Extracted Text:")
print(text)

from extract_info import extract_fields

fields = extract_fields(text)
print("\n📑 Extracted Fields:")
for k, v in fields.items():
    print(f"{k}: {v}")
