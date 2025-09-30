FROM python:3.12.3

WORKDIR /app

# Copy .dockerignore to ensure Docker uses it properly
COPY .dockerignore .dockerignore

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
