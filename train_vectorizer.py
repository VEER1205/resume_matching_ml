import os
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer


# ---------- LOAD CORPUS ----------
def load_corpus():
    texts = []
    folders = ["Text_data/resume", "Text_data/jd"]

    for folder in folders:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if file_path.endswith(".txt"):
                with open(file_path, "r", encoding="utf-8") as f:
                    texts.append(f.read())

    return texts


# ---------- FIT TF-IDF ----------
corpus = load_corpus()

vectorizer = TfidfVectorizer(
    stop_words="english",
    max_features=5000
)

vectorizer.fit(corpus)


# ---------- SAVE (FREEZE) ----------
with open("tfidf_vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)


print("TF-IDF fitted and IDF frozen successfully.")
print("Vocabulary size:", len(vectorizer.vocabulary_))
