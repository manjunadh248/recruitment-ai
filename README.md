# RecruitAI

AI-powered recruitment optimization platform that dynamically personalizes resumes, scores ATS compatibility, matches jobs, and optimizes application strategies.

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 20+ (for local frontend dev)
- Python 3.12+ (for local backend dev)

### Run with Docker
```bash
docker-compose up --build
```

### Services
| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| MongoDB | localhost:27017 |
| Redis | localhost:6379 |

### Local Development

**Backend:**
```bash
cd backend
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Architecture
See [docs/architecture.md](docs/architecture.md) for full system diagrams.

## Tech Stack
- **Frontend:** Next.js 15, shadcn/ui, Recharts
- **Backend:** FastAPI, Pydantic, Motor (async MongoDB)
- **AI:** spaCy, sentence-transformers, OpenAI/Gemini
- **Database:** MongoDB 7, Redis 7
- **DevOps:** Docker, Docker Compose
