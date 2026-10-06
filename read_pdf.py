import pdfplumber

PDF_FILE = "living world.pdf"

with pdfplumber.open(PDF_FILE) as pdf:
    print(f"Total pages: {len(pdf.pages)}\n")
    for i, page in enumerate(pdf.pages):
        print(f"\n===== PAGE {i+1} =====")
        text = page.extract_text()
        print(text if text else "[No text found - scanned image?]")
