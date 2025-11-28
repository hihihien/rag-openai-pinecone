FROM python:3.10-slim
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first
COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy backend code
COPY . .

EXPOSE 8000

# uvicorn server
CMD ["uvicorn", "serve_api:app", "--host", "0.0.0.0", "--port", "8000"]