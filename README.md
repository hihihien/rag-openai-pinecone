# MMI-Hien-2025

# KIM Backend Deployment Guide (FastAPI + Docker)

This document explains how to build and deploy the backend for the KIM RAG-Chatbot on the university server.  
The frontend is static and hosted separately; only the backend runs in Docker.


## 1. Overview

The backend is a FastAPI application that provides:

- `/ask` endpoint for chatbot responses  
- Retrieval-Augmented Generation (Pinecone vector search + OpenAI API)  
- Optional Supabase logging  
- Basic Authentication for production at HSD

The backend container listens on port **8000**, and is exposed via the reverse proxy: https://api.kim.app.medien.hs-duesseldorf.de/

## 2. Server Requirements

- Docker  
- Docker Compose  
- A `.env` file containing the required secrets  
- OpenAI and Pinecone API keys (provided by the project owner)


## 3. Project Structure
## 4. Environment Variables

Create a `.env` file in the same directory as `docker-compose.yml`. Check the `.env.example`, you might just need to add the correct valuable and change to `.env`. 

Notes:

- Only `BASIC_AUTH_USER` and `BASIC_AUTH_PASS` are needed for the backend at runtime.
- `NEXT_PUBLIC_*` variables are only necessary when the static frontend is built.


## 5. Start the Backend (Production)

Run: `docker compose up --build -d`


This will:

1. Build the backend from `backend/Dockerfile`
2. Load environment variables from `.env`
3. Start the FastAPI service on port 8000

Verify the backend:

http://localhost:8000/docs


The public endpoint via reverse proxy (given by Pogscheba Patrick):

https://api.kim.app.medien.hs-duesseldorf.de/

## 6. Basic Authentication

The `/ask` endpoint is protected using HTTP Basic Auth.

The backend reads credentials from:
`BASIC_AUTH_USER`
`BASIC_AUTH_PASS`

The static frontend sends the correct `Authorization: Basic ...` header automatically.

## 7. Logging

Local logs are saved to: backend/logs/chat_log.jsonl

With Supabase credentials configured from `.env`, the backend also uploads logs to the `chat_logs` table.  
Without Supabase configuration, logs are stored locally only.

## 8. Updating the Backend

Pull updates and rebuild:

```
git pull
docker compose build backend
docker compose up -d
```

Or rebuild everything completely:
```
docker compose down
docker compose up --build -d
```

## 9. Troubleshooting

### “next: not found”
This is from the old frontend Docker setup.  
The frontend is not deployed via Docker, so this message is not relevant, can be ignored.

### 401 Unauthorized (Basic Auth)
Check and correct credentials in `.env`:
```
BASIC_AUTH_USER
BASIC_AUTH_PASS
```
### OpenAI or Pinecone errors

Ensure all required API keys are present in `.env`. Contact me if any doubts for keys.

## 10. Summary for backend deployment 

1. Place project on the server  
2. Create `.env` containing all required variables based on `.env.example`  
3. Run `docker compose up --build -d`  
4. Confirm backend runs internally on port 8000  
5. Ensure reverse proxy forwards HTTPS traffic to the backend  
6. No frontend deployment is needed here (already static and hosted)

