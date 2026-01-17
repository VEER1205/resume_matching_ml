import re
import pickle
from sklearn.metrics.pairwise import cosine_similarity


# ---------------- LOAD FROZEN TF-IDF ----------------
with open("tfidf_vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)


# ---------------- NORMALIZATION ----------------
def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ---------------- SKILL CANON ----------------
SKILLS = [
    # Programming
    "python", "java", "api", "c++",

    # Data skills
    "data analysis", "exploratory data analysis", "eda",
    "data cleaning", "data preprocessing", "feature engineering",

    # ML core
    "machine learning", "supervised learning", "unsupervised learning",
    "linear regression", "logistic regression",
    "decision trees", "random forest", "clustering",

    # NLP
    "natural language processing", "nlp",
    "tf idf", "bag of words", "text similarity", "cosine similarity",

    # Libraries
    "scikit learn", "sklearn", "pandas", "numpy",
    "matplotlib", "seaborn",

    # Data storage
    "sql", "mysql", "postgresql", "database", "data warehouse",

    # MLOps
    "fastapi", "api", "model deployment",
    "docker", "ml pipeline", "model serving",

    # Optional
    "statistics", "probability",
    "hypothesis testing", "a b testing", "data visualization"
]


# ---------------- SKILL EXTRACTION ----------------
def extract_skills(text: str) -> set:
    text = normalize_text(text)
    found = set()

    for skill in SKILLS:
        if skill in text:
            found.add(skill)

    return found


# ---------------- SKILL OVERLAP ----------------
def calculate_skill_overlap(jd_text: str, resume_text: str):
    jd_skills = extract_skills(jd_text)
    resume_skills = extract_skills(resume_text)

    matched = jd_skills & resume_skills
    missing = jd_skills - resume_skills

    overlap_score = len(matched) / len(jd_skills) if jd_skills else 0.0

    return matched, missing, overlap_score


# ---------------- MAIN INFERENCE FUNCTION ----------------
def match_resume(jd_text: str, resume_text: str) -> dict:
    vectors = vectorizer.transform([jd_text, resume_text])

    cosine_score = float(
        cosine_similarity(vectors[0], vectors[1])[0][0]
    )

    matched, missing, skill_overlap = calculate_skill_overlap(
        jd_text, resume_text
    )
    COSINE_weight = 0.5
    SKILL_weight = 0.5

    final_score = COSINE_weight* cosine_score + SKILL_weight* skill_overlap

    return {
        "final_score": round(final_score, 3),
        "cosine_similarity": round(cosine_score, 3),
        "skill_overlap": round(skill_overlap, 3),
        "matched_skills": sorted(list(matched)),
        "missing_skills": sorted(list(missing))
    }

