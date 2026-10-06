import subprocess
import re
import json
import os

PDF_FILE = "biological classification.pdf"
OUTPUT_DIR = "output-bio"

# ============================================================
# STEP 1: pdftotext se pura text nikaalo
# ============================================================
print("📄 Extracting text from PDF...")
result = subprocess.run(
    ['pdftotext', '-layout', PDF_FILE, '-'],
    capture_output=True, text=True
)
all_lines = result.stdout.split('\n')
print(f"✅ Total {len(all_lines)} lines extracted\n")

# ============================================================
# STEP 2: Sections identify karo
# ============================================================
exercise_starts = {}   # {"1.1": 1, "1.2": 76, ...}
answer_starts = {}     # {"1.1": 687, "1.2": 694, ...}

in_answers = False
for i, line in enumerate(all_lines):
    s = line.strip()
    
    if 'ANSWER KEYS' in s:
        in_answers = True
        continue
    
    # "Exercise 1.1" ya "Exercise 4 (Previous Year's Questions)"
    m = re.match(r'Exercise\s+([\d.]+)', s)
    if m and len(s) < 60:
        ex = m.group(1)
        if in_answers:
            answer_starts[ex] = i
        else:
            exercise_starts[ex] = i

print(f"📚 Questions sections: {list(exercise_starts.keys())}")
print(f"🔑 Answer sections:    {list(answer_starts.keys())}\n")

# ============================================================
# STEP 3: Answer Key parse karo
# ============================================================
def parse_answer_key(lines, start, end):
    """Answer key se {qnum: answer} nikaalo"""
    answers = {}
    que_nums = []
    
    for line in lines[start:end]:
        s = line.strip()
        
        # "Que. 1 2 3 4 5 6 7 8 9 10"
        if s.startswith('Que.'):
            que_nums = [int(x) for x in re.findall(r'\d+', s[4:])]
        
        # "Ans. 4 2 1 3 4 2 4 4 2 2"
        elif s.startswith('Ans.'):
            ans_vals = [int(x) for x in re.findall(r'\d+', s[4:])]
            for q, a in zip(que_nums, ans_vals):
                answers[q] = a
    
    return answers

# Har exercise ki answer list banao
answer_keys = {}
sorted_ans = sorted(answer_starts.items(), key=lambda x: x[1])
for idx, (ex, start) in enumerate(sorted_ans):
    end = sorted_ans[idx + 1][1] if idx + 1 < len(sorted_ans) else len(all_lines)
    answer_keys[ex] = parse_answer_key(all_lines, start, end)
    print(f"🔑 Exercise {ex}: {len(answer_keys[ex])} answers")

print()

# ============================================================
# STEP 4: Questions parse karo
# ============================================================
def parse_questions(lines, start, end):
    """Questions section se questions nikaalo"""
    questions = []
    current_q = None
    current_opt = None
    
    for line in lines[start:end]:
        # Skip page markers
        if 'The Living World' in line or line.strip() == 'Biology':
            continue
        
        s = line.strip()
        if not s:
            continue
        
        # Naya question? "16. What is..."
        m = re.match(r'^(\d+)\.\s+(.+)', s)
        if m:
            if current_q:
                if current_opt:
                    current_q['options'][current_opt[0]] = current_opt[1]
                questions.append(current_q)
            current_q = {
                'num': int(m.group(1)),
                'text': m.group(2).strip(),
                'options': {}
            }
            current_opt = None
            continue
        
        # Naya option? "(1) Author's name..."
        m = re.match(r'^\((\d)\)\s*(.*)', s)
        if m and current_q:
            if current_opt:
                current_q['options'][current_opt[0]] = current_opt[1]
            current_opt = [int(m.group(1)), m.group(2).strip()]
            continue
        
        # Continuation line
        if current_opt:
            current_opt[1] += ' ' + s
        elif current_q:
            current_q['text'] += ' ' + s
    
    # Last question
    if current_q:
        if current_opt:
            current_q['options'][current_opt[0]] = current_opt[1]
        questions.append(current_q)
    
    return questions

# Har exercise ke questions
all_questions = {}
sorted_q = sorted(exercise_starts.items(), key=lambda x: x[1])
for idx, (ex, start) in enumerate(sorted_q):
    end = sorted_q[idx + 1][1] if idx + 1 < len(sorted_q) else min(answer_starts.values(), default=len(all_lines))
    questions = parse_questions(all_lines, start, end)
    all_questions[ex] = questions
    print(f"📝 Exercise {ex}: {len(questions)} questions")

print()

# ============================================================
# STEP 5: Answers attach karo
# ============================================================
for ex, questions in all_questions.items():
    ans = answer_keys.get(ex, {})
    for q in questions:
        q['answer'] = ans.get(q['num'], None)

# ============================================================
# STEP 6: JSON save karo (backup)
# ============================================================
os.makedirs(OUTPUT_DIR, exist_ok=True)
with open(f'{OUTPUT_DIR}/data.json', 'w', encoding='utf-8') as f:
    json.dump(all_questions, f, ensure_ascii=False, indent=2)
print(f"✅ data.json saved\n")

# ============================================================
# STEP 7: HTML files generate karo
# ============================================================
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Exercise {ex} - The Living World</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, 'Segoe UI', Arial, sans-serif; background: #f0f2f5; padding: 15px; line-height: 1.6; }}
        .container {{ max-width: 800px; margin: 0 auto; background: #fff; padding: 20px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); }}
        h1 {{ color: #1a1a2e; border-bottom: 3px solid #4f46e5; padding-bottom: 10px; margin-bottom: 20px; font-size: 20px; }}
        .back {{ display: inline-block; margin-bottom: 15px; color: #4f46e5; text-decoration: none; font-weight: 600; font-size: 14px; }}
        .question {{ background: #f9fafb; padding: 15px; margin-bottom: 15px; border-radius: 8px; border-left: 4px solid #4f46e5; }}
        .qtext {{ font-weight: 600; margin-bottom: 12px; color: #1a1a2e; }}
        .option {{ display: block; padding: 10px 12px; margin: 6px 0; background: #fff; border: 2px solid #e5e7eb; border-radius: 6px; cursor: pointer; transition: all 0.15s; font-size: 14px; }}
        .option:hover {{ border-color: #4f46e5; }}
        .option input {{ margin-right: 8px; }}
        .option.correct {{ background: #d1fae5; border-color: #10b981; }}
        .option.wrong {{ background: #fee2e2; border-color: #ef4444; }}
        .btn {{ background: #4f46e5; color: #fff; padding: 8px 16px; border: none; border-radius: 6px; cursor: pointer; font-size: 13px; margin-top: 8px; }}
        .btn:disabled {{ opacity: 0.5; cursor: not-allowed; }}
        .answer {{ display: none; margin-top: 10px; padding: 10px; background: #d1fae5; border-radius: 6px; color: #065f46; font-weight: 600; font-size: 14px; }}
        .answer.show {{ display: block; }}
        .footer {{ text-align: center; margin-top: 30px; color: #6b7280; font-size: 13px; }}
        .footer a {{ color: #4f46e5; text-decoration: none; margin: 0 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <a href="index.html" class="back">← All Exercises</a>
        <h1>Exercise {ex} - The Living World</h1>
        {questions_html}
        <div class="footer">
            {nav}
        </div>
    </div>
    <script>
        function checkAnswer(btn) {{
            const q = btn.closest('.question');
            const correct = parseInt(q.dataset.answer);
            const selected = q.querySelector('input[type="radio"]:checked');
            if (!selected) {{ alert('Pehle option select karo!'); return; }}
            q.querySelectorAll('.option').forEach(o => o.classList.remove('correct', 'wrong'));
            q.querySelectorAll('.option').forEach(o => {{
                const val = parseInt(o.querySelector('input').value);
                if (val === correct) o.classList.add('correct');
                if (o.querySelector('input').checked && val !== correct) o.classList.add('wrong');
            }});
            q.querySelector('.answer').classList.add('show');
            btn.disabled = true;
            btn.textContent = '✓ Answered';
        }}
    </script>
</body>
</html>'''

def make_question_html(q):
    opts = ''
    for num in [1, 2, 3, 4]:
        if num in q['options']:
            opts += f'<label class="option"><input type="radio" name="q{q["num"]}" value="{num}"> ({num}) {q["options"][num]}</label>\n'
    
    ans_text = ''
    if q['answer'] and q['answer'] in q['options']:
        ans_text = f"✅ Sahi jawab: ({q['answer']}) {q['options'][q['answer']]}"
    else:
        ans_text = "⚠️ Answer key me nahi mila"
    
    return f'''
    <div class="question" data-answer="{q['answer'] or 0}">
        <div class="qtext">Q{q['num']}. {q['text']}</div>
        {opts}
        <button class="btn" onclick="checkAnswer(this)">Check Answer</button>
        <div class="answer">{ans_text}</div>
    </div>'''

# Har exercise ki HTML
exercise_list = list(all_questions.keys())
for idx, (ex, questions) in enumerate(all_questions.items()):
    qhtml = '\n'.join(make_question_html(q) for q in questions)
    
    # Navigation
    nav = ''
    if idx > 0:
        prev = exercise_list[idx - 1]
        nav += f'<a href="exercise-{prev}.html">← Exercise {prev}</a>'
    nav += '<a href="index.html">🏠 Home</a>'
    if idx < len(exercise_list) - 1:
        nxt = exercise_list[idx + 1]
        nav += f'<a href="exercise-{nxt}.html">Exercise {nxt} →</a>'
    
    html = HTML_TEMPLATE.format(ex=ex, questions_html=qhtml, nav=nav)
    
    filename = f'{OUTPUT_DIR}/exercise-{ex}.html'
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✅ {filename}")

# ============================================================
# STEP 8: Index page
# ============================================================
index_links = ''
for ex, questions in all_questions.items():
    count = len(questions)
    answered = sum(1 for q in questions if q['answer'])
    index_links += f'<li><a href="exercise-{ex}.html"><span class="ex">Exercise {ex}</span><span class="meta">{count} questions • {answered} answered</span></a></li>\n'

index_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Living World - All Exercises</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, 'Segoe UI', Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }}
        .container {{ max-width: 600px; margin: 30px auto; background: #fff; padding: 25px; border-radius: 16px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); }}
        h1 {{ color: #1a1a2e; text-align: center; margin-bottom: 8px; }}
        .subtitle {{ text-align: center; color: #6b7280; margin-bottom: 25px; font-size: 14px; }}
        ul {{ list-style: none; }}
        li {{ margin-bottom: 10px; }}
        li a {{ display: flex; justify-content: space-between; align-items: center; padding: 15px 18px; background: #f9fafb; border-radius: 10px; text-decoration: none; color: #1a1a2e; border-left: 4px solid #4f46e5; transition: all 0.2s; }}
        li a:hover {{ background: #eef2ff; transform: translateX(5px); }}
        .ex {{ font-weight: 700; }}
        .meta {{ font-size: 12px; color: #6b7280; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📚 The Living World</h1>
        <p class="subtitle">Choose an exercise to begin</p>
        <ul>
            {index_links}
        </ul>
    </div>
</body>
</html>'''

with open(f'{OUTPUT_DIR}/index.html', 'w', encoding='utf-8') as f:
    f.write(index_html)
print(f"✅ {OUTPUT_DIR}/index.html")

print(f"\n🎉 DONE! Check '{OUTPUT_DIR}/' folder")

