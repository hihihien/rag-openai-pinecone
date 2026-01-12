# MMI-Hien-2025

# KIM - RAG-Chatbot für den Fachbereich Medien (Hochschule Düsseldorf)

KIM ist ein KI-gestützter Chatbot, der für den Fachbereich Medien (FBM) an der Hochschule Düsseldorf (HSD) entwickelt wurde.
Er basiert auf einer Retrieval-Augmented Generation (RAG)-Architektur und beantwortet Fragen zu Studiengängen, Modulen und weiteren studienrelevanten Themen auf Basis offizieller Dokumente und Webseiten. Das System wurde im Rahmen einer Masterarbeit im Studiengang Medieninformatik entwickelt und untersucht, wie RAG-basierte Chatbots Studierende beim Zugriff auf hochschulische Informationsquellen unterstützen können.

## Übersicht

KIM ermöglicht es Studierenden, Fragen in natürlicher Sprache zu stellen und präzise, kontextbasierte Antworten zu erhalten, die auf folgenden Quellen beruhen:

- Offizielle Modulhandbücher (PDF- und JSON-Daten)
- Webseiten der Studiengänge und des Fachbereichs

Jede Antwort enthält eine Quellenangabe, um die Nachvollziehbarkeit zu gewährleisten. Der Chatbot kann direkt auf den Studiengangsseiten eingebettet werden und bietet so einen einfachen, barrierearmen Zugang zu relevanten Informationen.

## Systemarchitektur
  
Das System folgt einer modularen Architektur, die in drei Schichten unterteilt ist.

### 1. Frontend (Next.js) + Marmann Hosting via FileZilla

- Interaktive Interface: `frontend/app/components/Chatbot.tsx`
- Studiengangsspezifische Begrüßungen und Beispielanfragen in `chatbotContext.ts`
- `lightbox_chat.js` ermöglicht die Einbettung als Chat Fenster auf den Webseiten
- Wird als statisches Exportprojekt auf dem Server des Fachbereichs gehostet `marmann.hosting.medien.hs-duesseldorf.de`, wird via FileZilla hochgeladen.
- Kommuniziert mit dem Backend über die Umgebungsvariable `NEXT_PUBLIC_API_URL` im `frontend\next.config.hsd.mjs`

### 2. Backend

Zuständig für KI-Verarbeitung, Datenabruf und Kontextaufbau
Zentrale Komponenten im Ordner backend/services/:
embeddings.py – Erzeugt Text-Embeddings mit OpenAI
pinecone_search.py – Führt Ähnlichkeitssuchen in Pinecone durch
context_builder.py – Baut den strukturierten Kontext aus den gefundenen Textabschnitten
prompt_utils.py – Sendet die Anfrage mit Kontext an das Sprachmodell (gpt-4.1-mini)
logger.py – Protokolliert Benutzeranfragen und Antworten (lokal und optional in Supabase)
loader.py – Lädt die bereinigten JSONL-Daten in den Speicher
Gehostet auf Render als Docker-Container
Bietet eine /ask-Schnittstelle für Chat-Anfragen

### 3. Daten und Vektordatenbank

Datenquellen:
Modulhandbücher (PDF + JSON)
Webseiten der Studiengänge und des Fachbereichs
Nach der Bereinigung werden sie in `/backend/data/merged/` und `/backend/data/processed_web/` als .jsonl-Dateien gespeichert
Vektorisiert mit OpenAI’s `text-embedding-3-large`
Speicherung in Pinecone, aufgeteilt nach Studiengangs-Namespace (z. B. BMI, MMI_WEB, FBM_WEB)

## Einrichtung und Installation

### 1. Repository Clone

git clone https://projectbase.medien.hs-duesseldorf.de/marmann/mmi-hien-2025
cd kim-rag-chatbot

### 2. Umgebungsvariablen konfigurieren

Erstelle eine `.env-Datei` im Root Directory:

`OPENAI_API_KEY=dein_openai_api_key
PINECONE_API_KEY=dein_pinecone_api_key
PINECONE_INDEX=kim-index
SUPABASE_URL=deine_supabase_url
SUPABASE_KEY=dein_supabase_key
NEXT_PUBLIC_API_URL=https://kim-chatbot.onrender.com
`
### 3. Dependencies installieren

#### Backend

`cd backend
pip install -r requirements.txt`

#### Frontend

`cd frontend
npm install`

### 4. Lokaler Start mit Docker

`docker-compose up --build`

Backend läuft auf: `http://localhost:8000`

Frontend läuft auf: `http://localhost:3000`

### 5. Statisches Frontend exportieren

`cd frontend
npm run build
npm run export
`

Das exportierte Frontend befindet sich anschließend im Ordner /frontend/out und kann auf jeden Webserver hochgeladen werden.

## Deployment

### 1. Backend:
- Bereitstellung über Render mithilfe der Dockerfile.
- Auf der kostenlosen Tier von Render kann es nach längerer Inaktivität zu Startverzögerungen (ca. 10–20 s) kommen.

### 2. Frontend:
- xportierte statische Dateien werden per FileZilla auf den Server von Prof. Marmann hochgeladen. Credentials wird sich von Professor Björn Nilson gegeben lassen.

### 3. Vektordatenbank:
- Gehostet auf Pinecone, aufgeteilt in Namespaces nach Studiengang.

## Zukunftsperspektive: Gemeinsames Hosting auf HSD-Servern
Langfristig kann das gesamte System (Backend + Frontend) vollständig auf einem universitären Server des Fachbereichs Medien betrieben werden.
Dadurch entfällt die Abhängigkeit von externen Cloud-Diensten (Render) und es entsteht eine nachhaltige, intern kontrollierte Infrastruktur.

### Vorschlag für die Integration

#### 1. Docker Compose als einheitliche Lösung

Der folgende Eintrag in `docker-compose.yml` definiert beide Dienste gemeinsam:

`services:
  backend:
    build:
      context: ./backend
    ports:
      - "8000:8000"
    env_file:
      - .env

  frontend:
    build:
      context: ./frontend
    ports:
      - "3000:3000"
    command: ["npm", "start"]
`


#### 2. Reverse Proxy (z. B. Nginx oder Apache)

Der Proxy kann beide Services unter einer gemeinsamen Domain in 2 Port verfügbar machen, eine für api backend, eine für frontend:

https://kim.medien.hs-duesseldorf.de/api → Backend (Port 8000)
https://kim.medien.hs-duesseldorf.de/    → Frontend (Port 3000)


#### 3. Sicherheit und Zugriff

- SSL-Zertifikate über das HSD-IT-Team
- Basic Auth (Vorschlag von Herr Patrick Pogscheba)

#### 4. Vorteile dieser Lösung

- Einheitliche Wartung und Backups
- Volle Datenhoheit innerhalb der Hochschule
- Keine externen Startverzögerungen (wie Cold Start und Timedown in Render) oder API-Timeouts
- Erweiterbar für zukünftige Chatbots und Anwendungen des FBM

## Zukünftige Erweiterungen (wenn nötig)

- Anbindung von mehrere Daten (Prüfungszeiten, Bewerbungsfristen, Abschlussarbeiten, usw.) 
- Automatische Datenaktualisierung und Versionsverwaltung Prozess verbessern
- Optimierung der Embeddings und Retrieval Prozess sowie Qualität der Generation mit mehrerer Test für verschiedene Werte von Parameters
- Erweiterte Nutzerstudien mit größerer User Gruppe (auch mit Professorinnen, Professoren und Mitarbeitenden des FBM)

## Lizenz

Dieses Projekt wurde im Rahmen einer Masterarbeit an der Hochschule Düsseldorf (HSD), Fachbereich Medien entwickelt. Die Nutzung ist zu Forschungs- und Lehrzwecken gestattet.