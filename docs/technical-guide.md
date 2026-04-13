# Clarion Technical Guide

## Architecture Overview
Clarion is a modular monolith built with FastAPI (Python 3.12+) on the backend and React 18 + TypeScript on the frontend. It uses PostgreSQL 16 for persistence, Redis 7 for caching and task queues, Celery 5 for async processing, and Ollama for local AI inference.

## Module Registry Pattern
Every feature is a self-contained module that registers its routes, schemas, events, and chatbot tools via a manifest. Modules are discovered at startup, dependencies resolved, and activated in order. Feature flags enable/disable modules without code changes.

## Data Flow
Salesforce → SF CLI → Sync Service → PostgreSQL → API → React Frontend
AI requests → AI Router → (Local: Ollama/Gemma4) or (External: Anonymise → Claude/OpenAI → De-anonymise) → Response

## Database
6 Alembic migrations create 30+ tables across 6 domains: identity, case data, review/intelligence, anonymisation, notifications, and configuration. Run migrations with: `alembic upgrade head`

## Docker Compose
7 containers: clarion-api, clarion-frontend, clarion-db, clarion-redis, clarion-worker, clarion-scheduler, clarion-ollama. Start with: `docker compose up -d`

## API Documentation
FastAPI auto-generates OpenAPI docs at `/api/docs` (development mode). 10 route groups: Health, Auth, Admin, Appearance, Preferences, Intelligence, Analytics, Predictions, Notifications, Chatbot.

## AI Engines
- **Ollama/Gemma4** (local): sentiment, predictions, chatbot, anonymisation Stage 4. No data leaves the system.
- **Claude Opus 4.6** (external): quality reviews, technical assessments. Data anonymised before transmission.
- **OpenAI** (external): alternative engine. Same anonymisation requirements.

## Anonymisation
4-stage pipeline: regex → dictionary → NER (spaCy) → LLM context review (Gemma4). Type-preserving pseudonymisation (PERSON_001, ORG_003). Bidirectional mapping for round-trip de-anonymisation. Zero-tolerance leak detection tests in CI.
