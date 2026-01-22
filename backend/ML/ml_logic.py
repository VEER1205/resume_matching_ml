import re
import pickle
from sklearn.metrics.pairwise import cosine_similarity
import os

# Get the absolute path of the directory where ml_logic.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PKL_PATH = os.path.join(BASE_DIR, "tfidf_vectorizer.pkl")

# ---------------- LOAD FROZEN TF-IDF ----------------
with open(PKL_PATH, "rb") as f:
    vectorizer = pickle.load(f)


# ---------------- NORMALIZATION ----------------
def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ---------------- SKILL CANON ----------------
SKILLS = [
    # --- Programming Languages ---
    "python", "java", "c++", "c", "c#", 
    "go", "golang", "rust", "ruby", "php", 
    "javascript", "typescript", "r", "scala", "julia",

    # --- Data Analysis & Core ---
    "data analysis", "exploratory data analysis", "eda",
    "data cleaning", "data preprocessing", "feature engineering",
    "data mining", "data wrangling", "statistics", "probability",
    "hypothesis testing", "a b testing", "bayesian statistics",
    "excel", "spreadsheet",

    # --- Machine Learning (Core) ---
    "machine learning", "supervised learning", "unsupervised learning",
    "reinforcement learning", "semi supervised learning",
    "linear regression", "logistic regression", "xgboost", "lightgbm", "catboost",
    "decision trees", "random forest", "gradient boosting", "svm", "support vector machines",
    "clustering", "k means", "dbscan", "pca", "dimensionality reduction",
    "ensemble methods", "hyperparameter tuning", "grid search", "random search",

    # --- Deep Learning ---
    "deep learning", "neural networks", "ann", 
    "pytorch", "tensorflow", "keras", "fastai",
    "cnn", "convolutional neural networks", 
    "rnn", "lstm", "gru", "transformers", "bert", "vision transformer",

    # --- Generative AI & LLMs ---
    "generative ai", "genai", "large language models", "llm",
    "rag", "retrieval augmented generation", "langchain", "llamaindex",
    "hugging face", "prompt engineering", "fine tuning", "lora", "qlora",
    "openai api", "stable diffusion",

    # --- NLP ---
    "natural language processing", "nlp", "nlu", "nlg",
    "tf idf", "bag of words", "word embeddings", "word2vec", "glove",
    "text similarity", "cosine similarity", "sentiment analysis",
    "named entity recognition", "ner", "tokenization", "lemmatization",
    "spacy", "nltk", "gensim",

    # --- Computer Vision ---
    "computer vision", "opencv", "image processing",
    "object detection", "yolo", "image segmentation", "ocr",

    # --- Libraries & Science ---
    "scikit learn", "sklearn", "pandas", "numpy", "scipy",
    "matplotlib", "seaborn", "plotly", "bokeh", "altair", "streamlit", "gradio",

    # --- Data Engineering & Big Data ---
    "sql", "mysql", "postgresql", "sqlite", "oracle", "sql server",
    "nosql", "mongodb", "redis", "cassandra", "dynamodb",
    "database", "data warehouse", "data lake",
    "apache spark", "pyspark", "hadoop", "kafka", 
    "airflow", "etl", "elt", "databricks", "snowflake", "bigquery", "redshift",

    # --- MLOps ---
    "mlops", "model deployment", "model serving", "model monitoring",
    "ml pipeline", "mlflow", "wandb", "weights and biases",
    "kubeflow", "ray", "triton",
    "docker", "kubernetes", "k8s", "containerization",

    # --- Backend ---
    "node js", "express js", "django", "flask", "fastapi",
    "spring boot", "ruby on rails", "asp net",
    "api", "rest api", "restful api", "graphql", "grpc", "websockets",
    "microservices", "serverless", "aws lambda",
    "celery", "rabbitmq",

    # --- Frontend ---
    "html", "html5", "css", "css3", "sass", "less",
    "react", "react js", "angular", "vue", "vue js",
    "next js", "redux", "state management",
    "tailwind css", "bootstrap", "material ui",
    "frontend", "web development", "responsive design",

    # --- Cloud & DevOps ---
    "aws", "amazon web services", "ec2", "s3", "rds", "sagemaker",
    "azure", "azure machine learning",
    "gcp", "google cloud platform", "vertex ai",
    "devops", "ci cd", "continuous integration", "continuous deployment",
    "jenkins", "github actions", "gitlab ci", "circleci",
    "terraform", "ansible",
    "git", "github", "gitlab", "bitbucket", "version control",
    "linux", "bash", "shell scripting", "command line"
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
    jd_text = normalize_text(jd_text)
    resume_text = normalize_text(resume_text)
    
    vectors = vectorizer.transform([jd_text, resume_text])

    cosine_score = float(
        cosine_similarity(vectors[0], vectors[1])[0][0]
    )

    matched, missing, skill_overlap = calculate_skill_overlap(
        jd_text, resume_text
    )
    COSINE_weight = 0.4
    SKILL_weight = 0.6

    final_score = COSINE_weight * cosine_score + SKILL_weight * skill_overlap

    return {
        "final_score": final_score,
        "cosine_similarity": cosine_score,
        "skill_overlap": skill_overlap,
        "matched_skills": sorted(list(matched)),
        "missing_skills": sorted(list(missing))
    }

