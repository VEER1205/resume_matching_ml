# 1. Use an official lightweight Python image
FROM python:3.9-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy requirements first (for better caching)
COPY requirements.txt .

# 4. Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Download the Spacy model (CRITICAL STEP)
# We do this during the build so the app doesn't crash on startup
RUN python -m spacy download en_core_web_sm

# 6. Copy the rest of your application code
COPY . .

# 7. Expose the port the app runs on
EXPOSE 8000

# 8. Command to run the app
# --host 0.0.0.0 is required for Docker containers to be accessible
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]