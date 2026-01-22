import os
import shutil
import json
import re
import pdfplumber
import google.generativeai as genai
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# --- 1. SETUP & CONFIG ---
load_dotenv()

# Import your local ML logic
from ML.ml_logic import match_resume

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# GEMINI SETUP
# Make sure GEMINI_API_KEY is in your .env file
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("⚠️ WARNING: GEMINI_API_KEY not found. Skills extraction might fail.")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# CORS (Allows Frontend to talk to Backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. HELPER FUNCTIONS ---

def extract_text_from_pdf(file_path):
    """Extracts raw text from PDF using pdfplumber."""
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    except Exception as e:
        print(f"❌ Error reading PDF: {e}")
    return text

def extract_skills_with_gemini(text):
    """
    Uses Gemini to extract skills.
    Includes REGEX fixing to handle cases where Gemini adds markdown formatting.
    """
    try:
        # Strict prompt to force JSON format
        prompt = f"""
        You are an expert Resume Parser. 
        Analyze the resume text below and extract a list of specific technical skills (Languages, Frameworks, Tools, Databases).
        
        RULES:
        1. Return ONLY a raw JSON list of strings. 
        2. Example output: ["Python", "Java", "AWS", "SQL", "React"]
        3. Do NOT include the word "json" or any markdown formatting.
        
        RESUME TEXT:
        {text[:10000]} 
        """
        
        response = model.generate_content(prompt)
        raw_text = response.text
        
        # --- FIX: Regex to find the JSON list inside the text ---
        # This grabs everything between [ and ] even if there is extra text around it
        match = re.search(r'\[.*\]', raw_text, re.DOTALL)
        
        if match:
            json_str = match.group(0)
            return json.loads(json_str)
        else:
            # Fallback cleanup
            cleaned = raw_text.strip().replace("```json", "").replace("```", "")
            return json.loads(cleaned)

    except Exception as e:
        print(f"❌ Gemini Extraction Error: {e}")
        return []

# --- 3. API ENDPOINT ---

@app.post("/match")
async def match_endpoint(
    job_description: str = Form(...),
    file: UploadFile = File(...)
):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        # A. Extract Text
        resume_text = extract_text_from_pdf(file_path)
        
        if not resume_text.strip():
            return {"status": "error", "message": "Could not extract text from PDF (it might be an image)."}

        # B. Run ML Logic (Calculates Score + Missing Skills)
        ml_result = match_resume(job_description, resume_text)
        
        # C. Run Gemini Logic (Extracts Candidate Skills)
        extracted_skills = extract_skills_with_gemini(resume_text)
        
        # --- FALLBACK MECHANISM ---
        # If Gemini fails (returns empty), use the skills found by the ML model
        if not extracted_skills:
            print("⚠️ Gemini returned empty skills. Falling back to ML keywords.")
            extracted_skills = ml_result.get("matched_skills", [])

        # D. Return Final Response
        return {
            "status": "success",
            "filename": file.filename,
            "data": {
                "match_percentage": round(ml_result.get("final_score", 0) * 100, 2),
                "extracted_skills": extracted_skills,
                "missing_skills": ml_result.get("missing_skills", [])
            }
        }

    except Exception as e:
        print(f"❌ Critical Error: {str(e)}")
        return {"status": "error", "message": str(e)}
        
    finally:
        # Cleanup temp file
        if os.path.exists(file_path):
            os.remove(file_path)

@app.get("/")
def home():
    return {"message": "Resume Matcher API is Running"}