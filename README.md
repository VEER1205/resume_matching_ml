# Resume Matcher (Hybrid ML-Based Ranking System)

## Overview
This project ranks resumes against a given job description using a hybrid approach that combines
explicit skill overlap and textual similarity. The system provides a relative relevance ranking
and does not classify candidates as job-ready or not.

---

## Problem Statement
Traditional keyword-based resume matching fails when skills are phrased differently or implied
indirectly. This project addresses that limitation by combining rule-based skill matching with
ML-based text similarity.

---

## Approach
The final ranking score is computed using two signals:

1. Skill Overlap  
   - Extracts predefined technical skills from both the job description and resume  
   - Measures how many required skills are present in the resume  

2. Textual Similarity  
   - Uses TF-IDF vectorization on normalized text  
   - Computes cosine similarity between the job description and resume  

The final score is a weighted combination of both signals:

final_score = w1 * cosine_similarity + w2 * skill_overlap


Higher scores indicate stronger alignment between the resume and the job description.

---

## What This System Does
- Ranks resumes by relevance to a job description
- Handles indirect and differently phrased skill mentions
- Provides interpretable outputs such as matched and missing skills

---

## What This System Does NOT Do
- Does not classify resumes as job-ready
- Does not make hiring decisions
- Does not measure candidate quality or seniority

Scores are relative, not probabilities.

---

## Project Structure
.
├── ml_logic.py
├── test_matcher.py
├── tfidf_vectorizer.pkl
├── requirements.txt
└── README.md


---

## How to Run

1. Install dependencies:
pip install -r requirements.txt


2. Run the test script:
python test_matcher.py

---

## Sample Output
Strong match: 0.52
Partial match: 0.39
Weak match: 0.29


Higher-ranked resumes are more aligned with the job description.

---

## Evaluation Logic
The system is evaluated by verifying that resumes with stronger alignment consistently rank
higher than partial or weak matches for the same job description.

---

## Limitations
- TF-IDF has limited semantic understanding
- Skill extraction is rule-based
- Scores depend on resume wording and structure

---

## Future Improvements
- Replace TF-IDF with sentence embeddings
- Improve skill normalization and synonym handling
- Add score calibration for UI display