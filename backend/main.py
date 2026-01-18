import os
import shutil
import pdfplumber
import spacy
from spacy.matcher import PhraseMatcher
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware

# --- IMPORT ML LOGIC ---
from ML.ml_logic import match_resume

app = FastAPI()

# --- CONFIGURATION ---
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 1. Load Spacy
nlp = spacy.load("en_core_web_sm")

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- YOUR CUSTOM SKILLS DB ---
SKILLS_DB = [
    # Languages
    "Python", "Java", "C++", "C", "JavaScript", "HTML", "CSS", "SQL", "MySQL",
    # Frameworks & Libraries
    "FastAPI", "Django", "Express.js", "Node.js", "React", "Custom Tkinter", 
    "KivyMD", "Tkinter", "PyGame", "Google Gen AI APIs", "Google Gen AI",
    # Tools & Platforms
    "Git", "GitHub", "Visual Studio Code", "Jupyter Notebook", "Postman", 
    "AWS", "Docker", "Linux",
    # Concepts / Other
    "RESTful APIs", "JWT Authentication", "Object-Oriented Programming", 
    "Machine Learning", "Data Structures", "Algorithms", "Data Visualization"
]

# --- HELPER FUNCTIONS ---
def extract_text_from_pdf(file_path):
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text

def extract_skills_with_spacy(text):
    """
    Extracts skills using YOUR custom list (SKILLS_DB).
    """
    doc = nlp(text)
    matcher = PhraseMatcher(nlp.vocab)
    
    # Create patterns
    patterns = [nlp.make_doc(skill) for skill in SKILLS_DB]
    matcher.add("SKILLS", patterns)
    
    matches = matcher(doc)
    found_skills = set()
    
    for _, start, end in matches:
        found_skills.add(doc[start:end].text)
        
    return list(found_skills)

# --- API ENDPOINT ---
@app.post("/match")
async def match_endpoint(
    job_description: str = Form(...),
    file: UploadFile = File(...)
):
    # 1. Save file temporarily
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        # 2. Extract Raw Text (For the ML Model)
        resume_text = extract_text_from_pdf(file_path)
        
        # 3. Extract Specific Skills (For the JSON Output)
        my_custom_skills = extract_skills_with_spacy(resume_text)
        
        # 4. Get Score from ML Model
        # We pass the full text so the ML model can do TF-IDF math
        ml_result = match_resume(job_description, resume_text)
        
        # 5. Merge the results
        # We overwrite the ML model's simple skills with YOUR custom spacy skills
        return {
            "status": "success",
            "filename": file.filename,
            "data": {
                "match_percentage": round(ml_result["final_score"] * 100, 2),
                "extracted_skills": my_custom_skills,  # <--- HERE are your specific skills
                "missing_skills": ml_result["missing_skills"]
            }
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
        
    finally:
        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)

@app.get("/")
def home():
    return {"message": "Resume Matcher API is Running"}