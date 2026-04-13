# Clarion

**Intelligent Support Analytics Platform**

Clarion transforms raw Salesforce case data into proactive, actionable intelligence for support managers. AI-powered analytics, quality reviews, predictive case intelligence, and an integrated chatbot — delivered through an enterprise-grade, white-label platform.

## Architecture

- **Frontend:** React 18 + TypeScript + Tailwind CSS + shadcn/ui
- **Backend:** FastAPI (Python 3.12) + SQLAlchemy + Alembic
- **Database:** PostgreSQL 16
- **Cache/Queue:** Redis 7 + Celery 5
- **AI:** Ollama (Gemma4 local) + Claude API + OpenAI API
- **Deployment:** Docker Compose (V1), Kubernetes-ready (V2)

### Key Design Patterns

- **Module Registry:** Features self-register routes, UI, permissions, and chatbot tools. New modules added without modifying existing code.
- **DataScope Abstraction:** Pluggable data filtering at the repository layer. V1 ships TeamScope + AccountScope; V2 extends to Region, Product, Org scopes.
- **4 Default Roles:** Admin (org scope), Manager (team + account toggle), CSM (account, read-only), Accounts (same as CSM, terminology customised).
- **Contract Testing:** Inter-module API contracts validated on every CI build. Breaking changes caught at PR time.
- **AI-First Reviews:** AI generates complete case review drafts; managers refine with tracked overrides.
- **Salesforce Validated:** All field mappings validated against Octave production org via SOQL queries.

## Quick Start

### Prerequisites

- Docker Desktop (Apple Silicon Mac)
- Git

### Setup

```bash
# Clone
git clone https://github.com/your-org/clarion.git
cd clarion

# Configure
cp .env.example .env
# Edit .env — set CLARION_DB_PASSWORD and CLARION_JWT_SECRET

# Launch
docker compose up -d

# Pull Gemma4 model (first time only)
docker exec clarion-ollama ollama pull gemma2

# Run migrations
docker exec clarion-api alembic upgrade head

# Access
open https://localhost
```

### Development

```bash
# Backend (outside Docker)
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (outside Docker)
cd frontend
npm install
npm run dev

# Run tests
cd backend && pytest tests/ -v
cd frontend && npm test
```

## Project Structure

```
clarion/
├── .github/workflows/ci.yml    # CI pipeline
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app factory
│   │   ├── config.py            # Pydantic settings
│   │   ├── registry.py          # Module registry
│   │   ├── scopes.py            # DataScope abstraction
│   │   ├── api/v1/routes/       # Core routes (auth, health, admin)
│   │   ├── modules/             # Feature modules (self-registering)
│   │   │   ├── accounts/
│   │   │   ├── cases/
│   │   │   ├── reviews/
│   │   │   ├── analytics/
│   │   │   ├── predictions/
│   │   │   ├── notifications/
│   │   │   ├── chatbot/
│   │   │   ├── anonymisation/
│   │   │   └── sync/
│   │   ├── intelligence/        # AI orchestration
│   │   ├── integrations/        # External services
│   │   └── middleware/          # Auth, CORS, audit
│   ├── alembic/                 # Database migrations
│   └── tests/
│       ├── unit/
│       ├── integration/
│       ├── contracts/           # Inter-module contract tests
│       └── anonymisation/       # PII leak detection
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   └── moduleRegistry.ts  # Frontend module registry
│   │   ├── modules/             # Feature modules (mirror backend)
│   │   ├── stores/              # Zustand global state
│   │   └── theme/               # White-label + dark mode
│   └── nginx.conf               # Reverse proxy config
├── docs/                        # PRD, Architecture, SDS
├── docker-compose.yml
└── .env.example
```

## Documentation

| Document | Description |
|----------|-------------|
| [PRD v1.3](docs/) | Product Requirements Document |
| [System Architecture v1.3](docs/) | Architecture decisions, container design, security |
| [SDS v1.2](docs/) | Database schema, API contracts, UI specification |

## Build Phases

| Phase | Name | Status |
|-------|------|--------|
| 0 | Project Setup | ✅ Complete |
| 1 | Frontend Shell | 🔲 Next |
| 2 | Authentication & RBAC | 🔲 |
| 3 | Salesforce Sync & Data Layer | 🔲 |
| 4 | Anonymisation Engine | 🔲 |
| 5 | AI Integration | 🔲 |
| 6 | Case Review Framework | 🔲 |
| 7 | Analytics & Predictions | 🔲 |
| 8 | Notifications & Alerting | 🔲 |
| 9 | Chatbot | 🔲 |
| 10 | Admin Completion | 🔲 |
| 11 | Documentation | 🔲 |
| 12 | Security & Pen Test | 🔲 |
| 13 | QA & Release | 🔲 |

## License

Proprietary. All rights reserved.
