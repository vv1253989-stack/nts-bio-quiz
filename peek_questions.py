import pdfplumber
import re

PDF_FILE = "living world.pdf"

with pdfplumber.open(PDF_FILE) as pdf:
    # Page 5 se 13 tak dekho (jahan questions hain, theory ke baad)
    for i in range(5, 14):
        if i >= len(pdf.pages):
            break
        text = pdf.pages[i].extract_text()
        if not text:
            continue
        
        # Exercise headings dhundo
        if 'Exercise' in text or re.search(r'^\d+\.\s', text, re.MULTILINE):
            print(f"\n{'='*60}")
            print(f"PAGE {i+1}")
            print('='*60)
            print(text)
            print(f"\n{'='*60}\n")
            break  # Sirf pehla questions page dikhao

