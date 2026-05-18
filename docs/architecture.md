# RecruitAI — System Architecture

## High-Level Architecture

```mermaid
graph TB
    subgraph Client["🖥️ Frontend (Next.js 15)"]
        UI[Dashboard UI]
        Auth_UI[Auth Pages]
    end

    subgraph Gateway["🔒 API Gateway"]
        CORS[CORS]
        RateLimit[Rate Limiter]
        JWT_Auth[JWT Auth]
    end

    subgraph Backend["⚡ FastAPI Backend"]
        AuthAPI[Auth API]
        ResumeAPI[Resume API]
        ATSAPI[ATS API]
        PersonalizeAPI[Personalize API]
        JobsAPI[Jobs API]
    end

    subgraph AIEngine["🧠 AI Engine"]
        Parser[Resume Parser]
        ATSScorer[ATS Scorer]
        Personalizer[Resume Personalizer]
        Matcher[Job Matcher]
    end

    subgraph Data["💾 Data Layer"]
        MongoDB[(MongoDB)]
        Redis[(Redis Cache)]
        FileStore[File Storage]
    end

    subgraph External["🌐 External"]
        OpenAI[OpenAI API]
        Gemini[Gemini API]
        JobBoards[Job Boards]
    end

    Client --> Gateway --> Backend
    Backend --> AIEngine
    Backend --> Data
    AIEngine --> External
    AIEngine --> Data
```

## Service Communication Flow

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Next.js Frontend
    participant API as FastAPI Backend
    participant AI as AI Engine
    participant DB as MongoDB
    participant LLM as OpenAI/Gemini

    U->>FE: Upload Resume
    FE->>API: POST /api/v1/resume/upload
    API->>AI: Parse Resume
    AI->>AI: Extract Text (PyMuPDF)
    AI->>AI: NER (spaCy)
    AI->>AI: Embeddings (SBERT)
    AI->>DB: Store Parsed Data
    API->>FE: Return Parsed Resume

    U->>FE: Score Against Job
    FE->>API: POST /api/v1/ats/score
    API->>AI: ATS Analysis
    AI->>AI: Extract JD Keywords
    AI->>AI: Semantic Similarity
    AI->>AI: Calculate Score
    AI->>DB: Store ATS Score
    API->>FE: Return Score + Suggestions

    U->>FE: Personalize Resume
    FE->>API: POST /api/v1/personalize/generate
    API->>AI: Personalize
    AI->>LLM: Rewrite Sections
    AI->>AI: Generate PDF
    AI->>DB: Store Version
    API->>FE: Return Personalized Resume
```

## Database Architecture

```mermaid
erDiagram
    USERS ||--o{ RESUMES : uploads
    USERS ||--o| SKILL_PROFILES : has
    RESUMES ||--o{ ATS_SCORES : scored_against
    RESUMES ||--o{ OPTIMIZED_RESUMES : personalized_into
    JOBS ||--o{ ATS_SCORES : scored_for
    JOBS ||--o{ JOB_MATCHES : matched_to
    JOBS ||--o{ OPTIMIZED_RESUMES : tailored_for
    USERS ||--o{ JOB_MATCHES : receives

    USERS {
        ObjectId _id PK
        string email UK
        string name
        string password_hash
        datetime created_at
    }

    RESUMES {
        ObjectId _id PK
        ObjectId user_id FK
        string raw_text
        object parsed_data
        string file_path
        boolean is_primary
    }

    JOBS {
        ObjectId _id PK
        string title
        string company
        string description
        array skills_required
        string source
    }

    ATS_SCORES {
        ObjectId _id PK
        ObjectId resume_id FK
        ObjectId job_id FK
        float overall_score
        array missing_keywords
    }

    OPTIMIZED_RESUMES {
        ObjectId _id PK
        ObjectId user_id FK
        ObjectId job_id FK
        object personalized_content
        string pdf_path
        int version
    }

    JOB_MATCHES {
        ObjectId _id PK
        ObjectId user_id FK
        ObjectId job_id FK
        float match_score
        array skill_overlap
    }

    SKILL_PROFILES {
        ObjectId _id PK
        ObjectId user_id FK
        array skills
        array embeddings
    }
```

## Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | Next.js 15, shadcn/ui, Recharts | Dashboard UI |
| Backend | FastAPI, Pydantic, Uvicorn | REST API |
| Database | MongoDB 7 (Motor async) | Document storage |
| Cache | Redis 7 | Sessions, caching |
| AI/NLP | spaCy, sentence-transformers, KeyBERT | Text analysis |
| LLM | OpenAI GPT-4 / Google Gemini | Content generation |
| PDF | WeasyPrint | Resume PDF generation |
| Auth | JWT (python-jose), bcrypt | Authentication |
| Containers | Docker, Docker Compose | Development & deployment |
