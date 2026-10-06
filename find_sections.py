import subprocess

# pdftotext se pura text nikaalo
result = subprocess.run(
    ['pdftotext', '-layout', 'living world.pdf', '-'],
    capture_output=True, text=True
)
text = result.stdout
lines = text.split('\n')

# Exercise aur ANSWER KEYS dhundo
print("=" * 60)
print("IMPORTANT LINES (page markers, exercises, answer keys)")
print("=" * 60)

for i, line in enumerate(lines):
    stripped = line.strip()
    if any(kw in stripped for kw in ['Exercise', 'ANSWER', 'Answer Key']):
        print(f"Line {i:4d} | {stripped[:80]}")
    
    # Page break markers
    if 'The Living World' in stripped and 'Biology' in stripped:
        print(f"Line {i:4d} | [PAGE MARKER] {stripped[:80]}")

