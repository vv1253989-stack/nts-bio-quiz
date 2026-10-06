import pdfplumber

PDF_FILE = "living world.pdf"

with pdfplumber.open(PDF_FILE) as pdf:
    for i, page in enumerate(pdf.pages):
        print(f"\n{'='*50}")
        print(f"PAGE {i+1}")
        print('='*50)
        text = page.extract_text()
        if text:
            # Har line ke saath line number print karo
            for j, line in enumerate(text.split('\n')):
                print(f"{j:3d} | {line}")
