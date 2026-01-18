from ml_logic import match_resume

jd = """
Role: Backend / ML Engineer

Requirements:
Strong Python programming
Experience building REST APIs
Familiarity with machine learning concepts
Experience with data preprocessing and model deployment
Knowledge of FastAPI or Flask preferred
SQL and basic cloud exposure is a plus
"""

resume_strong = """
Software Engineer with 2 years of experience in Python-based backend systems.

Built RESTful APIs using FastAPI and Flask for data-driven applications
Designed and deployed machine learning models for text classification
Implemented data preprocessing pipelines using Pandas and NumPy
Integrated ML models into backend services for real-time inference
Worked with PostgreSQL and basic AWS services for deployment
"""

resume_partial = """
Backend Developer with experience in Python and web services.

Developed backend services using Django and Flask
Built and maintained REST APIs for web applications
Worked with relational databases and wrote complex SQL queries
"""

resume_weak = """
Data Science student with basic exposure to machine learning.

Completed online courses in ML
Worked on small academic datasets
No backend or API development experience
"""

print("Strong match:", match_resume(jd, resume_strong))
print("Partial match:", match_resume(jd, resume_partial))
print("Weak match:", match_resume(jd, resume_weak))