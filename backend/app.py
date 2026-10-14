from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from pypdf import PdfReader
from collections import Counter
from math import sqrt
from docx import Document
from flask_login import (LoginManager,UserMixin,login_user,logout_user,login_required,current_user)
from werkzeug.security import (generate_password_hash,check_password_hash)
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from io import BytesIO
import json
import re
import zipfile
import xml.etree.ElementTree as ET

app = Flask(__name__)

app.config["SECRET_KEY"] = "ai-resume-analyzer-secret-key"
CORS(
    app,
    supports_credentials=True,
    origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ]
)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///resume_analyzer.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

SKILLS = ["python","java","javascript","c","c++","c#","php",
          "html","css","react","node.js","node","express","flask","django",
          "mysql","sql","mongodb","postgresql","oracle",
          "machine learning","deep learning","artificial intelligence","data science","data analysis","pandas","numpy","tensorflow","pytorch","scikit-learn","nlp",
          "git","github","docker","postman","linux",
          "aws","azure","google cloud",
          "rest api","api","oop","data structures","algorithms"]

class Analysis(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    resume_filename = db.Column(db.String(255))
    job_description = db.Column(db.Text)
    score = db.Column(db.Integer)
    semantic_score = db.Column(db.Integer)
    skill_score = db.Column(db.Integer)
    length_score = db.Column(db.Integer)
    section_score = db.Column(db.Integer)
    word_count = db.Column(db.Integer)
    job_role = db.Column(db.String(255))
    matching_skills = db.Column(db.Text)
    missing_skills = db.Column(db.Text)
    suggestions = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)

def extract_pdf_text(file):
    reader = PdfReader(file)

    text = ""

    print("PDF pages:",len(reader.pages))

    for page_number,page in enumerate(reader.pages):
        page_text = page.extract_text()

        print(
            f"Page {page_number + 1}: "
            f"{len(page_text or '')} characters"
        )

        if page_text:
            text += page_text + "\n"

    return text


def extract_docx_text(file):

    try:
        file.stream.seek(0)

        # Read DOCX as ZIP file
        with zipfile.ZipFile(file.stream) as docx_zip:

            text_parts = []

            # --------------------------------
            # Read main document.xml
            # --------------------------------
            if "word/document.xml" in docx_zip.namelist():

                xml_data = docx_zip.read("word/document.xml")

                root = ET.fromstring(xml_data)

                namespace = {
                    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
                }

                for paragraph in root.findall(".//w:p", namespace):

                    paragraph_text = []

                    for text_node in paragraph.findall(
                        ".//w:t",
                        namespace
                    ):
                        if text_node.text:
                            paragraph_text.append(
                                text_node.text
                            )

                    text = "".join(paragraph_text).strip()

                    if text:
                        text_parts.append(text)

            # --------------------------------
            # Read headers and footers
            # --------------------------------
            for filename in docx_zip.namelist():

                if (
                    filename.startswith("word/header")
                    or filename.startswith("word/footer")
                ):

                    if filename.endswith(".xml"):

                        xml_data = docx_zip.read(filename)

                        root = ET.fromstring(xml_data)

                        namespace = {
                            "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
                        }

                        for text_node in root.findall(
                            ".//w:t",
                            namespace
                        ):

                            if text_node.text:
                                text = text_node.text.strip()

                                if text:
                                    text_parts.append(text)

        # Remove duplicates while keeping order
        unique_text = []

        for text in text_parts:

            if text not in unique_text:
                unique_text.append(text)

        final_text = "\n".join(unique_text)

        print("=" * 50)
        print("DOCX EXTRACTION")
        print("Characters:", len(final_text))
        print("Words:", len(final_text.split()))
        print("Preview:")
        print(final_text[:1000])
        print("=" * 50)

        return final_text

    except Exception as e:

        print("DOCX EXTRACTION ERROR:", str(e))

        return ""

def extract_resume_text(file):

    if not file or not file.filename:
        return ""

    filename = file.filename.lower().strip()

    print("Uploaded file:",filename)

    if filename.endswith(".pdf"):
        print("PDF detected")
        text = extract_pdf_text(file)

    elif filename.endswith(".docx"):
        print("DOCX detected")
        text = extract_docx_text(file)

    else:
        print("Unsupported file type")
        return ""

    print("Extracted characters:",len(text))

    return text

def extract_skills(text):
    text_lower = text.lower()
    found_skills = []

    for skill in SKILLS:
        pattern = r"\b" + re.escape(skill) + r"\b"

        if re.search(pattern,text_lower):
            found_skills.append(skill)

    return sorted(set(found_skills))

def calculate_score(resume_skills,job_skills):
    if not job_skills:
        return 0

    matched = set(resume_skills).intersection(set(job_skills))

    score = (len(matched) / len(job_skills)) * 100

    return round(score)

def generate_suggestions(resume_skills,job_skills,resume_text):
    suggestions = []
    missing =set(job_skills) - set(resume_skills)

    if missing:
        suggestions.append("Consider adding relevant missing skills:"
                           + ", ".join(sorted(missing)[:5]))

    if len(resume_text.split()) < 150:
        suggestions.append(
            "Your resume appears short. "
            "Consider adding relevant projects, "
            "experience and achievements."
        )

    if "project" not in resume_text.lower():
        suggestions.append(
            "Add a projects section with technologies"
            "and measurable results."
        )

    if "github" not in resume_text.lower():
        suggestions.append(
            "Consider adding your github profile"
            "and relevant repositories."
        )

    if not suggestions:
        suggestions.append(
            "Your resume contains many relevant skills."
            "Continue improving project description "
            "with measurable achievements"
        )

    return suggestions

def extract_name(text):
    lines = [
        line.strip() 
        for line in text.split("\n")
        if line.strip()
    ]
    
    for line in lines[:10]:
        if(
            "@" not in line
            and not re.search(r"\d", line)
            and len(line.split()) <= 5
            and len(line) < 50
        ):
            return line
        
    return "Not detected"

def extract_email(text):
    
    match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)

    if match:
        return match.group()
    return "Not detected"

def extract_phone(text):
    match = re.search(r"(?:\+91[\s-]?)?[6-9]\d{9}", text)

    if match:
        return match.group()
    return "Not detected"

def extract_education(text):
    
    education_keywords = [
        "b.tech", "btech", "b.e", "be", "m.tech", "mtech", "m.e", "me", "bca", "mca", "b.sc", "m.sc", "bachelor", "master", "diploma", "degree"
    ]
    
    lines = text.split("\n")
    
    education = []
    
    for line in lines:
        
        line_clean = line.strip()
        line_lower = line_clean.lower()
        
        if any(keyword in line_lower for keyword in education_keywords):
            education.append(line_clean)
    
    return education[:10]  # Return first 10 entries

def extract_experience(text):
    
    lines = text.split("\n")
    experience = []
    keywords = [
        "intern", "internship", "developer", "engineer", "software engineer", "software developer", "experience", "worked at", "employment"
    ]
    
    for line in lines:
        line_clean = line.strip()
        line_lower = line_clean.lower()
        
        if any(keyword in line_lower for keyword in keywords):
            experience.append(line_clean)
    
    return experience[:15]  # Return first 15 entries

def extract_projects(text):
    
    lines = text.split("\n")
    projects = []
    keywords = [
        "project", "developed", "developing", "application", "website", "system", "chatbot", "analyzer"
    ]
    
    for line in lines:
        line_clean = line.strip()
        line_lower = line_clean.lower()
        
        if any(keyword in line_lower for keyword in keywords):
            projects.append(line_clean)
    
    return projects[:15]  # Return first 15 entries

def extract_certifications(text):

    lines = text.split("\n")

    certifications = []

    keywords = [
        "certification",
        "certified",
        "certificate",
        "coursera",
        "udemy",
        "nptel",
        "hackerrank",
        "google certificate"
    ]

    for line in lines:

        line_clean = line.strip()

        line_lower = line_clean.lower()

        if any(
            keyword in line_lower
            for keyword in keywords
        ):

            certifications.append(line_clean)

    return certifications[:10]

def extract_resume_information(text):
    return {

        "name":
        extract_name(text),

        "email":
        extract_email(text),

        "phone":
        extract_phone(text),

        "education":
        extract_education(text),

        "experience":
        extract_experience(text),

        "projects":
        extract_projects(text),

        "certifications":
        extract_certifications(text),

        "skills":
        extract_skills(text)
    }
     
def generate_ats_report(
    resume_text,
    resume_skills,
    job_skills,
    sections,
    semantic_score
):

    strengths = []
    improvements = []

    # -----------------------------
    # Strengths
    # -----------------------------

    matching_skills = set(
        resume_skills
    ).intersection(
        set(job_skills)
    )

    if matching_skills:
        strengths.append(
            f"Your resume contains {len(matching_skills)} "
            "skills relevant to the job."
        )

    if semantic_score >= 70:
        strengths.append(
            "Resume content has strong semantic "
            "alignment with the job description."
        )

    if sections.get("projects"):
        strengths.append(
            "Projects section detected."
        )

    if sections.get("education"):
        strengths.append(
            "Education section detected."
        )

    if sections.get("experience"):
        strengths.append(
            "Experience section detected."
        )

    # -----------------------------
    # Improvements
    # -----------------------------

    missing_skills = (
        set(job_skills)
        - set(resume_skills)
    )

    if missing_skills:
        improvements.append(
            "Consider adding relevant skills: "
            + ", ".join(
                sorted(missing_skills)[:8]
            )
        )

    if not sections.get("projects"):
        improvements.append(
            "Add a Projects section."
        )

    if not sections.get("experience"):
        improvements.append(
            "Add internship or work experience "
            "if applicable."
        )

    if not sections.get("education"):
        improvements.append(
            "Add your education details."
        )

    if not sections.get("skills"):
        improvements.append(
            "Add a clearly labelled Skills section."
        )

    if semantic_score < 60:
        improvements.append(
            "Tailor your resume wording more closely "
            "to the target job description."
        )

    # -----------------------------
    # ATS checklist
    # -----------------------------

    checklist = {

        "Contact Information":
            sections.get("contact", False),

        "Education":
            sections.get("education", False),

        "Experience":
            sections.get("experience", False),

        "Projects":
            sections.get("projects", False),

        "Skills":
            sections.get("skills", False),

        "Relevant Keywords":
            len(matching_skills) > 0
    }

    return {
        "strengths": strengths,
        "improvements": improvements,
        "checklist": checklist
    }
    

def calculate_semantic_similarity(resume_text, job_description):
    # Convert text to lowercase words
    resume_words = re.findall(r"\b[a-zA-Z0-9+#.]+\b", resume_text.lower())
    job_words = re.findall(r"\b[a-zA-Z0-9+#.]+\b", job_description.lower())

    if not resume_words or not job_words:
        return 0

    # Count the frequency of each word
    resume_vector = Counter(resume_words)
    job_vector = Counter(job_words)

    # Find common words
    common_words = set(resume_vector) & set(job_vector)

    dot_product = sum(
        resume_vector[word] * job_vector[word]
        for word in common_words
    )

    resume_magnitude = sqrt(
        sum(count * count for count in resume_vector.values())
    )

    job_magnitude = sqrt(
        sum(count * count for count in job_vector.values())
    )

    if resume_magnitude == 0 or job_magnitude == 0:
        return 0

    similarity = dot_product / (
        resume_magnitude * job_magnitude
    )

    return round(max(0, min(100, similarity * 100)))
def analyze_resume(resume_text, job_description):
    
    resume_information = extract_resume_information(resume_text)

    resume_skills = extract_skills(resume_text)

    job_skills = extract_skills(job_description)
    
    semantic_score = calculate_semantic_similarity(resume_text,job_description)

    matching_skills = list(set(resume_skills).intersection(
        job_skills)
    )

    missing_skills = list(set(job_skills) - set(resume_skills))

    score = calculate_score(resume_skills,job_skills)

    word_count = len(resume_text.split())

    if word_count >= 300:
        length_score = 100
    elif word_count >= 150:
        length_score = 80
    elif word_count >= 80:
        length_score = 60
    else:
        length_score = 40

    resume_lower = resume_text.lower()

    sections = {
        "education" : "education" in resume_lower,
        "experience" : "experience" in resume_lower,
        "projects" : "projects" in resume_lower,
        "skills" : "skills" in resume_lower,
        "contact" : ("@" in resume_text)

    }

    section_score = (sum(sections.values()) / len(sections)) * 100
    section_score = round(section_score)

    overall_score = round(
        (score * 0.60) + (length_score * 0.20) + (section_score * 0.20)
    )

    suggestions = generate_suggestions(resume_skills,job_skills,resume_text)
    
    ats_report = generate_ats_report(resume_text,resume_skills,job_skills,sections,semantic_score)

    if not sections["projects"]:
        suggestions.append(
            "Add a Projects section to demonstrate "
            "practical technical experience."
        )

    if not sections["education"]:
        suggestions.append(
            "Add your education details. "
        )
    if not sections["experience"]:
        suggestions.append(
            "Add intership or work experience if available. "
        )

    job_lower = job_description.lower()

    if "machine learning" in job_lower:
        job_role = "Machine Learning / AI Developer"

    elif "data analyst" in job_lower:
        job_role = "Data Analyst"

    elif "react" in job_lower:
        job_role = "Frontend Developer"

    elif "flask" in job_lower:
        job_role = "Python Backend Developer"

    elif "python" in job_lower:
        job_role = "Python Developer"

    else:
        job_role = "Software Developer"

    return {
        "score" : overall_score,
        "semantic_score" : semantic_score,
        "skill_score" : score,
        "length_score" : length_score,
        "section_score" : section_score,
        "word_count" : word_count,
        "job_role" : job_role,
        "resume_skills" : sorted(resume_skills),
        "job_skills" : sorted(job_skills),
        "matching_skills" : sorted(matching_skills),
        "missing_skills" : sorted(missing_skills),
        "sections" : sections,
        "suggestions" : suggestions,
        "resume_information" : resume_information,
        "ats_report" : ats_report

    }


def generate_pdf_report(result):
    
    buffer = BytesIO()
    
    document = SimpleDocTemplate(buffer, pagesize=A4,
                                 rightMargin=40, leftMargin=40, topMargin=60, bottomMargin=40)
    
    styles = getSampleStyleSheet()
    
    title_style = styles['Title']
    title_style.alignment = TA_CENTER
    
    heading_style = styles['Heading2']
    normal_style = styles['BodyText']
    
    story = []
    
    story.append(Paragraph("AI Resume Analyzer - Analysis Report", title_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Resume Information", heading_style))
    
    resume_info = [
        ["Resume", result.get("resume_filename", "N/A")],
        ["Job Role", result.get("job_role", "N/A")],
        ["Word Count", str(result.get("word_count", 0))],
        ["Overall Score", str(result.get("score", 0)) + "/100"]
    ]
    
    table = Table(resume_info, colWidths=[150, 350])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 8)
    ]))
    
    story.append(table)
    story.append(Spacer(1, 20))
    
    story.append(
        Paragraph(
            "Score Breakdown",
            heading_style
        )
    )

    scores = [
        ["Category", "Score"],
        [
            "Semantic Score",
            str(result.get("semantic_score", 0)) + "/100"
        ],
        [
            "Skill Score",
            str(result.get("skill_score", 0)) + "/100"
        ],
        [
            "Length Score",
            str(result.get("length_score", 0)) + "/100"
        ],
        [
            "Section Score",
            str(result.get("section_score", 0)) + "/100"
        ],
    ]

    score_table = Table(
        scores,
        colWidths=[250, 150]
    )

    score_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("PADDING", (0, 0), (-1, -1), 8),
        ])
    )

    story.append(score_table)

    story.append(Spacer(1, 20))

    # -----------------------------
    # MATCHING SKILLS
    # -----------------------------

    story.append(
        Paragraph(
            "Matching Skills",
            heading_style
        )
    )

    matching_skills = result.get(
        "matching_skills",
        []
    )

    if matching_skills:
        story.append(
            Paragraph(
                ", ".join(matching_skills),
                normal_style
            )
        )
    else:
        story.append(
            Paragraph(
                "No matching skills found.",
                normal_style
            )
        )

    story.append(Spacer(1, 15))

    # -----------------------------
    # MISSING SKILLS
    # -----------------------------

    story.append(
        Paragraph(
            "Missing Skills",
            heading_style
        )
    )

    missing_skills = result.get(
        "missing_skills",
        []
    )

    if missing_skills:
        story.append(
            Paragraph(
                ", ".join(missing_skills),
                normal_style
            )
        )
    else:
        story.append(
            Paragraph(
                "No missing skills found.",
                normal_style
            )
        )

    story.append(Spacer(1, 15))

    # -----------------------------
    # SUGGESTIONS
    # -----------------------------

    story.append(
        Paragraph(
            "Suggestions",
            heading_style
        )
    )

    suggestions = result.get(
        "suggestions",
        []
    )

    if suggestions:

        for suggestion in suggestions:

            story.append(
                Paragraph(
                    "• " + str(suggestion),
                    normal_style
                )
            )

            story.append(Spacer(1, 5))

    else:

        story.append(
            Paragraph(
                "No suggestions available.",
                normal_style
            )
        )

    # -----------------------------
    # BUILD PDF
    # -----------------------------

    document.build(story)

    buffer.seek(0)

    return buffer


@app.route("/")
def home():

    return jsonify({
        "message": "AI Resume Analyzer Backend is running!"
    })


@app.route("/analyze", methods=["POST"])
def analyze():

    try:

        if "resume" not in request.files:

            return jsonify({
                "error": "Resume file is required"
            }), 400


        resume_file = request.files["resume"]


        job_description = request.form.get(
            "job_description",
            ""
        )


        if  not job_description.strip():

            return jsonify({
                "error": "Job description is required"
            }), 400


        resume_text = extract_resume_text(
            resume_file
        )


        if not resume_text.strip():

            return jsonify({
                "error": "Could not extract resume text"
            }), 400


        result = analyze_resume(
            resume_text,
            job_description
        )
        
        result["resume_filename"] = resume_file.filename
        
        analysis = Analysis(
            resume_filename=resume_file.filename,
            job_description=job_description,
            score=result["score"],
            semantic_score=result["semantic_score"],
            skill_score=result["skill_score"],
            length_score=result["length_score"],
            section_score=result["section_score"],
            word_count=result["word_count"],
            job_role=result["job_role"],
            matching_skills=json.dumps(result["matching_skills"]),
            missing_skills=json.dumps(result["missing_skills"]),
            suggestions=json.dumps(result["suggestions"])
        )
        
        db.session.add(analysis)
        db.session.commit()

        return jsonify({
            "success": True,
            "message" : "Resume analyzed successfully",
            "result": result
        })
        
    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
        
@app.route("/download_report", methods=["POST"])
def download_report():
    
    try:
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        pdf_buffer = generate_pdf_report(data)
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name="AI_Resume_Analysis_Report.pdf",
            mimetype="application/pdf"
        )
    except Exception as e:
        
        print("PDF ERROR:", e)
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/history", methods=["GET"])
def history():
    
    analyses = Analysis.query.order_by(
        Analysis.created_at.desc()
    ).all()
    
    history_data = []
    
    for analysis in analyses:
        history_data.append({
            
            "id" : analysis.id,
            "resume_filename" : analysis.resume_filename,
            "score" : analysis.score,
            "semantic_score" : analysis.semantic_score,
            "skill_score" : analysis.skill_score,
            "length_score" : analysis.length_score,
            "section_score" : analysis.section_score,
            "word_count" : analysis.word_count,
            "job_role" : analysis.job_role,
            "matching_skills" : json.loads(analysis.matching_skills or "[]"),
            "missing_skills" : json.loads(analysis.missing_skills or "[]"),
            "suggestions" : json.loads(analysis.suggestions or "[]"),
            "created_at" : analysis.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })
        
    return jsonify({
        "success": True,
        "history": history_data
    })
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    name = data.get("name","").strip()
    email = data.get("email","").strip().lower()
    password = data.get("password","")

    if not name or not email or not password:
        return jsonify({"success": False, "error": "All fields are required"}), 400
    
    if len(password) < 6:
        return jsonify({"success": False, "error": "Password must be at least 6 characters"}), 400

    exiting_user = User.query.filter_by(email=email).first()
    if exiting_user:
        return jsonify({"success": False, "error": "Email already registered"}), 400

    hashed_password = generate_password_hash(password)
    
    user = User(name=name, email=email, password_hash=hashed_password)
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({"success": True, "message": "Account created successfully"})

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({
            "success": False,
            "error": "Email and password are required"
        }), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({
            "success": False,
            "error": "Invalid email or password"
        }), 401

    if not check_password_hash(user.password_hash, password):
        return jsonify({
            "success": False,
            "error": "Invalid email or password"
        }), 401

    login_user(user)

    return jsonify({
        "success": True,
        "message": "Login successful",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }), 200
@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"success": True, "message": "Logged out successfully"})

@app.route("/me", methods=["GET"])
def get_current_user():
    if not current_user.is_authenticated:
        return jsonify({"logged_in": False})
    
    return jsonify({
        "logged_in": True,
        "user": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email
        }
    })
with app.app_context():
    db.create_all()


if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        debug=True,
        port=5000
    )

