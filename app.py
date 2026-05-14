import gradio as gr
import pdfplumber
import docx
import re
import matplotlib.pyplot as plt

# =========================================================
# CAREER DATABASE
# =========================================================

career_database = {
    "AI Engineer": {
        "keywords": ["machine learning", "deep learning", "python", "tensorflow", "nlp"],
        "recommended_skills": ["TensorFlow", "PyTorch", "NLP", "Model Deployment"]
    },
    "Frontend Developer": {
        "keywords": ["html", "css", "javascript", "react"],
        "recommended_skills": ["React", "GitHub", "API Integration"]
    },
    "Data Analyst": {
        "keywords": ["sql", "excel", "power bi", "data analysis"],
        "recommended_skills": ["Power BI", "Tableau", "Statistics"]
    },
    "Doctor": {
        "keywords": ["doctor", "medical", "patient", "hospital"],
        "recommended_skills": ["Patient Care", "Medical Reporting"]
    },
    "Teacher": {
        "keywords": ["teacher", "education", "classroom"],
        "recommended_skills": ["Classroom Management", "Communication"]
    }
}

# =========================================================
# SKILLS DATABASE
# =========================================================

skills_db = [
    "python", "java", "c++", "machine learning", "deep learning",
    "html", "css", "javascript", "react", "sql",
    "excel", "power bi", "tableau", "nlp"
]

# =========================================================
# TEXT EXTRACTION
# =========================================================

def extract_text(file):
    text = ""

    if file.name.endswith(".pdf"):
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                if page.extract_text():
                    text += page.extract_text()

    elif file.name.endswith(".docx"):
        doc = docx.Document(file)
        for para in doc.paragraphs:
            text += para.text + "\n"

    return text

# =========================================================
# EMAIL
# =========================================================

def get_email(text):
    emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}", text)
    return emails[0] if emails else "Not Found"

# =========================================================
# PHONE
# =========================================================

def get_phone(text):
    phones = re.findall(r"\+?\d[\d -]{8,12}\d", text)
    return phones[0] if phones else "Not Found"

# =========================================================
# SKILLS
# =========================================================

def get_skills(text):
    text = text.lower()
    return [s for s in skills_db if s in text]

# =========================================================
# CAREER DETECTION
# =========================================================

def get_career(text):
    text = text.lower()
    best = "General"

    max_count = 0

    for career, data in career_database.items():
        count = sum(1 for k in data["keywords"] if k in text)

        if count > max_count:
            max_count = count
            best = career

    return best

# =========================================================
# MISSING SKILLS
# =========================================================

def get_missing(career, skills):
    if career not in career_database:
        return []

    rec = career_database[career]["recommended_skills"]
    return [s for s in rec if s.lower() not in skills]

# =========================================================
# EXPERIENCE
# =========================================================

def get_experience(text):
    text = text.lower()

    if "intern" in text or "fresher" in text:
        return "Fresher"
    elif "senior" in text or "5 years" in text:
        return "Senior"
    elif "2 years" in text or "3 years" in text:
        return "Mid Level"
    else:
        return "Unknown"

# =========================================================
# SCORE
# =========================================================

def get_score(skills, text):
    score = len(skills) * 10

    if "project" in text.lower():
        score += 10
    if "experience" in text.lower():
        score += 10
    if score > 100:
        score = 100

    return score

# =========================================================
# GRAPH
# =========================================================

def create_graph(score, skill_count):

    labels = ["Score", "Skills Score"]
    values = [score, skill_count * 10]

    fig, ax = plt.subplots()
    ax.bar(labels, values)
    ax.set_ylim(0, 100)
    ax.set_title("Resume Analysis Graph")

    return fig

# =========================================================
# MAIN FUNCTION
# =========================================================

def analyze(file):

    if file is None:
        return "Upload file", "", "", "", "", "", "", None

    text = extract_text(file)

    email = get_email(text)
    phone = get_phone(text)
    skills = get_skills(text)
    career = get_career(text)
    missing = get_missing(career, skills)
    exp = get_experience(text)
    score = get_score(skills, text)
    graph = create_graph(score, len(skills))

    result = (
        f"{score}/100",
        career,
        exp,
        email,
        phone,
        ", ".join(skills),
        ", ".join(missing),
        graph
    )

    return result

# =========================================================
# UI
# =========================================================

with gr.Blocks(theme=gr.themes.Soft()) as demo:

    gr.Markdown("# 📄 ResumeVision AI")

    file = gr.File(label="Upload Resume")

    btn = gr.Button("Analyze")

    with gr.Row():
        score = gr.Textbox(label="Score")
        career = gr.Textbox(label="Career")

    with gr.Row():
        exp = gr.Textbox(label="Experience")
        email = gr.Textbox(label="Email")

    with gr.Row():
        phone = gr.Textbox(label="Phone")
        skills = gr.Textbox(label="Skills")

    missing = gr.Textbox(label="Missing Skills")

    graph = gr.Plot(label="Graph")

    btn.click(
        analyze,
        inputs=file,
        outputs=[score, career, exp, email, phone, skills, missing, graph]
    )

demo.launch()
