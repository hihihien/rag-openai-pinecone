FROM python:3.10-slim

WORKDIR /app

# copy backend folder into /app/backend
COPY backend /app/backend

# copy requirements if it's in project root
COPY requirements.txt /app/

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

EXPOSE 8000

#package entrypoint
CMD ["uvicorn", "backend.serve_api:app", "--host", "0.0.0.0", "--port", "8000"]

