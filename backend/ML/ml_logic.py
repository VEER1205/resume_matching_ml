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



# ---------------- SKILL MAP ----------------
# ================================
# SKILL MAP
# Canonical Skill -> Alias Set
# ================================

SKILL_MAP = {

    # ------------------------------------------------
    # Core Concepts
    # ------------------------------------------------
    "machine learning": {"machine learning", "ml"},
    "deep learning": {"deep learning", "dl"},
    "natural language processing": {"natural language processing", "nlp"},
    "computer vision": {"computer vision", "cv"},
    "ci/cd": {"ci cd", "ci-cd", "continuous integration", "continuous deployment"},

    # ------------------------------------------------
    # Programming Languages
    # ------------------------------------------------
    "python": {"python"},
    "java": {"java"},
    "c": {"c"},
    "c++": {"c++"},
    "c#": {"c#"},
    "golang": {"go", "golang"},
    "rust": {"rust"},
    "ruby": {"ruby"},
    "php": {"php"},
    "javascript": {"javascript", "js"},
    "typescript": {"typescript", "ts"},
    "scala": {"scala"},
    "julia": {"julia"},

    # ------------------------------------------------
    # Data Analysis & Statistics
    # ------------------------------------------------
    "data analysis": {"data analysis"},
    "exploratory data analysis": {"exploratory data analysis", "eda"},
    "data cleaning": {"data cleaning"},
    "data preprocessing": {"data preprocessing"},
    "feature engineering": {"feature engineering"},
    "data mining": {"data mining"},
    "data wrangling": {"data wrangling"},
    "statistics": {"statistics"},
    "probability": {"probability"},
    "hypothesis testing": {"hypothesis testing"},
    "a/b testing": {"a b testing", "ab testing", "a/b testing"},
    "bayesian statistics": {"bayesian statistics"},
    "excel": {"excel"},
    "spreadsheets": {"spreadsheet", "spreadsheets"},

    # ------------------------------------------------
    # Machine Learning Algorithms
    # ------------------------------------------------
    "supervised learning": {"supervised learning"},
    "unsupervised learning": {"unsupervised learning"},
    "reinforcement learning": {"reinforcement learning"},
    "semi-supervised learning": {
        "semi supervised learning",
        "semi-supervised learning"
    },

    "linear regression": {"linear regression"},
    "logistic regression": {"logistic regression"},
    "decision trees": {"decision tree", "decision trees"},
    "random forest": {"random forest", "random forests"},
    "gradient boosting": {"gradient boosting"},
    "xgboost": {"xgboost"},
    "lightgbm": {"lightgbm"},
    "catboost": {"catboost"},

    "support vector machines": {
        "svm",
        "support vector machine",
        "support vector machines"
    },

    "clustering": {"clustering"},
    "k-means": {"k means", "k-means"},
    "dbscan": {"dbscan"},
    "dimensionality reduction": {"dimensionality reduction"},
    "pca": {"pca", "principal component analysis"},

    "ensemble methods": {"ensemble methods"},
    "hyperparameter tuning": {"hyperparameter tuning"},
    "grid search": {"grid search"},
    "random search": {"random search"},

    # ------------------------------------------------
    # Deep Learning Architectures
    # ------------------------------------------------
    "neural networks": {"neural networks", "neural network", "ann"},
    "convolutional neural networks": {
        "cnn",
        "convolutional neural network",
        "convolutional neural networks"
    },
    "recurrent neural networks": {
        "rnn",
        "recurrent neural network",
        "recurrent neural networks"
    },
    "lstm": {"lstm"},
    "gru": {"gru"},
    "transformers": {"transformers", "transformer"},
    "bert": {"bert"},
    "vision transformer": {"vision transformer", "vit"},

    # ------------------------------------------------
    # ML / DL Frameworks
    # ------------------------------------------------
    "pytorch": {"pytorch", "torch"},
    "tensorflow": {"tensorflow", "tf"},
    "keras": {"keras"},
    "fastai": {"fastai"},
    "scikit-learn": {"scikit learn", "scikit-learn", "sklearn"},

    # ------------------------------------------------
    # Generative AI & LLMs
    # ------------------------------------------------
    "generative ai": {"generative ai", "genai"},
    "large language models": {"large language models", "llm", "llms"},
    "retrieval augmented generation": {
        "rag",
        "retrieval augmented generation"
    },
    "langchain": {"langchain"},
    "llamaindex": {"llamaindex"},
    "hugging face": {"hugging face", "huggingface"},
    "prompt engineering": {"prompt engineering"},
    "fine tuning": {"fine tuning", "finetuning"},
    "lora": {"lora"},
    "qlora": {"qlora"},
    "openai api": {"openai api"},
    "stable diffusion": {"stable diffusion"},

    # ------------------------------------------------
    # NLP Techniques & Libraries
    # ------------------------------------------------
    "nlu": {"nlu"},
    "nlg": {"nlg"},
    "tf-idf": {"tf idf", "tf-idf"},
    "bag of words": {"bag of words", "bow"},
    "word embeddings": {"word embeddings"},
    "word2vec": {"word2vec"},
    "glove": {"glove"},
    "text similarity": {"text similarity"},
    "cosine similarity": {"cosine similarity"},
    "sentiment analysis": {"sentiment analysis"},
    "named entity recognition": {
        "named entity recognition",
        "ner"
    },
    "tokenization": {"tokenization"},
    "lemmatization": {"lemmatization"},
    "spacy": {"spacy"},
    "nltk": {"nltk"},
    "gensim": {"gensim"},

    # ------------------------------------------------
    # Computer Vision Tools
    # ------------------------------------------------
    "opencv": {"opencv"},
    "image processing": {"image processing"},
    "object detection": {"object detection"},
    "yolo": {"yolo"},
    "image segmentation": {"image segmentation"},
    "ocr": {"ocr"},

    # ------------------------------------------------
    # Data Engineering & Databases
    # ------------------------------------------------
    "sql": {"sql"},
    "mysql": {"mysql"},
    "postgresql": {"postgresql", "postgres"},
    "sqlite": {"sqlite"},
    "oracle": {"oracle"},
    "sql server": {"sql server"},
    "nosql": {"nosql"},
    "mongodb": {"mongodb"},
    "redis": {"redis"},
    "cassandra": {"cassandra"},
    "dynamodb": {"dynamodb"},
    "data warehouse": {"data warehouse"},
    "data lake": {"data lake"},
    "apache spark": {"apache spark", "spark"},
    "pyspark": {"pyspark"},
    "hadoop": {"hadoop"},
    "kafka": {"kafka"},
    "airflow": {"airflow"},
    "etl": {"etl"},
    "elt": {"elt"},
    "databricks": {"databricks"},
    "snowflake": {"snowflake"},
    "bigquery": {"bigquery"},
    "redshift": {"redshift"},

    # ------------------------------------------------
    # MLOps & DevOps
    # ------------------------------------------------
    "mlops": {"mlops"},
    "model deployment": {"model deployment"},
    "model serving": {"model serving"},
    "model monitoring": {"model monitoring"},
    "ml pipeline": {"ml pipeline"},
    "mlflow": {"mlflow"},
    "wandb": {"wandb", "weights and biases"},
    "kubeflow": {"kubeflow"},
    "ray": {"ray"},
    "triton": {"triton"},
    "docker": {"docker"},
    "kubernetes": {"kubernetes", "k8s"},
    "containerization": {"containerization"},

    # ------------------------------------------------
    # Backend, Frontend, Cloud
    # ------------------------------------------------
    "fastapi": {"fastapi"},
    "django": {"django"},
    "flask": {"flask"},
    "spring boot": {"spring boot"},
    "node.js": {"node js", "node.js"},
    "express.js": {"express js", "express.js"},
    "graphql": {"graphql"},
    "grpc": {"grpc"},
    "rest api": {"rest api", "restful api"},
    "websockets": {"websockets"},
    "microservices": {"microservices"},
    "serverless": {"serverless"},
    "aws lambda": {"aws lambda"},

    "react": {"react", "react js"},
    "angular": {"angular"},
    "vue": {"vue", "vue js"},
    "next.js": {"next js"},
    "redux": {"redux"},
    "tailwind css": {"tailwind css"},
    "bootstrap": {"bootstrap"},
    "material ui": {"material ui"},

    "aws": {"aws", "amazon web services"},
    "azure": {"azure", "azure machine learning"},
    "gcp": {"gcp", "google cloud platform"},
    "vertex ai": {"vertex ai"},
}




# ---------------- SKILL EXTRACTION ----------------
def extract_skills(text: str) -> set:
    text = normalize_text(text)
    found = set()

    for canonical, aliases in SKILL_MAP.items():
        for alias in aliases:
            pattern = r"\b" + re.escape(alias) + r"\b"
            if re.search(pattern, text):
                found.add(canonical)
                break   

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
    COSINE_weight = 0.5
    SKILL_weight = 0.5

    final_score = COSINE_weight * cosine_score + SKILL_weight * skill_overlap

    return {
        "final_score": final_score,
        "cosine_similarity": cosine_score,
        "skill_overlap": skill_overlap,
        "matched_skills": sorted(list(matched)),
        "missing_skills": sorted(list(missing))
    }

