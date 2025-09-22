FROM python:3.10-slim

WORKDIR /app

# copy backend folder into /app/backend
COPY .app

# copy requirements if it's in project root
COPY ./backend/requirements.txt /app/

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

EXPOSE 8000

#package entrypoint
CMD ["sh", "-c", "uvicorn serve_api:app --host 0.0.0.0 --port 8000"]

