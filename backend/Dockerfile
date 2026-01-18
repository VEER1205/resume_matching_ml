# 1. Use the slim image
FROM python:3.9-slim

# 2. Set working directory
WORKDIR /app

# --- FIX STARTS HERE ---
# 3. Install GCC and Build Tools (Required for Spacy/Blis)
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*
# --- FIX ENDS HERE ---

# 4. Copy requirements
COPY requirements.txt .

# 5. Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 6. Download Spacy model
RUN python -m spacy download en_core_web_sm

# 7. Copy the rest of the app
COPY . .

# 8. Expose port
EXPOSE 8000

# 9. Run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]