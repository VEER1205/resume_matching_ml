import os
import shutil
import json
import pdfplumber
import google.generativeai as genai  # <--- NEW IMPORT
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
load_dotenv()

# --- IMPORT ML LOGIC ---
# Assuming this is your local file
from ML.ml_logic import match_resume

app = FastAPI()

# --- CONFIGURATION ---
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- GEMINI SETUP ---
# Replace with your actual API Key or use os.getenv("GEMINI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") 
genai.configure(api_key=GEMINI_API_KEY)

# We use 'gemini-1.5-flash' as it is fast and cheap for text tasks
model = genai.GenerativeModel('gemini-1.5-flash')

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- HELPER FUNCTIONS ---
def extract_text_from_pdf(file_path):
    """
    Extracts raw text using pdfplumber to send to Gemini.
    """
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

def extract_skills_with_gemini(text):
    """
    Uses Gemini API to intelligently extract skills from the resume text.
    """
    try:
        # Prompt engineering to get a strict JSON list
        prompt = f"""
        You are an expert ATS (Applicant Tracking System). 
        Analyze the resume text provided below and extract all Technical Skills, 
        Programming Languages, Frameworks, Libraries, and Tools.
        
        Return ONLY a raw JSON list of strings. Do not add Markdown formatting (like ```json).
        
        RESUME TEXT:
        {text}
        """
        
        response = model.generate_content(prompt)
        
        # Clean the response to ensure it can be parsed as JSON
        cleaned_response = response.text.strip()
        
        # Handle cases where Gemini might still add markdown backticks
        if cleaned_response.startswith("```"):
            cleaned_response = cleaned_response.strip("`").replace("json", "").strip()

        skills_list = json.loads(cleaned_response)
        return skills_list

    except Exception as e:
        print(f"Gemini Extraction Error: {e}")
        return [] # Return empty list on failure

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
        # 2. Extract Raw Text (via pdfplumber)
        resume_text = extract_text_from_pdf(file_path)
        
        if not resume_text.strip():
            return {"status": "error", "message": "Could not extract text from PDF"}

        # 3. Extract Specific Skills (via GEMINI API)
        # This replaces the old Spacy method
        gemini_skills = extract_skills_with_gemini(resume_text)
        
        # 4. Get Score from ML Model
        # (Assuming your ML logic handles TF-IDF/Cosine Similarity)
        ml_result = match_resume(job_description, resume_text)
        
        # 5. Merge the results
        return {
            "status": "success",
            "filename": file.filename,
            "data": {
                "match_percentage": round(ml_result.get("final_score", 0) * 100, 2),
                "extracted_skills": gemini_skills,  # <--- Now powered by Gemini
                "missing_skills": ml_result.get("missing_skills", [])
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
    return {"message": "Resume Matcher API (Powered by Gemini) is Running"}