import pdfplumber

PDF_FILE = "living world.pdf"

with pdfplumber.open(PDF_FILE) as pdf:
    total = len(pdf.pages)
    print(f"Total pages: {total}\n")
    print("=" * 50)
    print("LAST 3 PAGES (Answer Key dhundhne ke liye)")
    print("=" * 50)
    for i in range(max(0, total - 3), total):
        print(f"\n--- PAGE {i+1} ---")
        print(pdf.pages[i].extract_text())

