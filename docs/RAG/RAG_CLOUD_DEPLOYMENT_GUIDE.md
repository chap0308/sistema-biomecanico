# RAG Cloud Deployment Guide

This document explains how to move the current biomechanics RAG system from local development into a cloud deployment, what services should live in the cloud, and which native dependencies still matter even when the app is no longer running on a personal machine.

## Goal

Deploy the system so that:

- the chat UI can call the backend remotely
- the backend can analyze supported inputs
- Supabase remains the system of record
- Qdrant Cloud serves retrieval
- external model providers can be used without depending on a local machine

## Repository strategy

For the current stage of the project, the recommended setup is to keep **two repositories**:

1. `sistema-biomecanico`
   - FastAPI backend
   - ingestion and analysis pipelines
   - Supabase persistence
   - Qdrant indexing and retrieval
   - operational scripts
2. `chat-fisioterapia`
   - Vite + React frontend
   - Supabase Auth client
   - chat UI
   - model selector
   - image upload flow

### Why two repositories are recommended now

- `Railway` and `Vercel` work more cleanly when frontend and backend are deployed independently
- each project has different environment variables
- each project has different build and runtime requirements
- CI and previews are easier to keep isolated
- the frontend can evolve as product UI while the backend remains the research and processing core

### Is a monorepo possible?

Yes, but it is not the best fit for the current phase.

A monorepo would make more sense later if:

- deployment pipelines become standardized
- shared packages appear
- frontend and backend release cycles need tighter coordination

For now, separate repositories are the simpler and safer path.

## Current cloud-ready pieces

These parts are already compatible with cloud deployment:

- `Supabase`
  - PostgreSQL database
  - Auth
  - Storage buckets
- `Qdrant Cloud`
  - `video_knowledge_units_v1`
  - `video_segments_v1`
- external model APIs
  - Gemini
  - Hugging Face Inference Providers
  - OpenAI

## What should run in the cloud

### 1. Backend API

The FastAPI backend should be deployed to a cloud runtime.

It is responsible for:

- chat endpoints
- image analysis orchestration
- RAG retrieval
- answer generation
- source ingestion workflows
- persistence to Supabase
- indexing to Qdrant

Relevant entrypoint:

- [main.py](/D:/sistema-biomecanico/app/main.py)

### 2. Qdrant

Qdrant does not need to be "lifted" locally anymore if the project is already pointed to Qdrant Cloud.

Use Qdrant Cloud for:

- vector storage
- hybrid retrieval
- production search access from the cloud backend

This is useful because:

- the UI and backend no longer depend on a local Qdrant process
- indexes survive machine restarts
- retrieval is available from remote environments

### 3. Supabase

Supabase is already the cloud system of record.

No extra migration to "Supabase cloud" is needed if you are already using a hosted Supabase project.

Supabase continues to store:

- users and auth sessions
- chat conversations and messages
- analysis attempts
- source metadata
- knowledge drafts
- knowledge units
- storage buckets for originals and debug images

### 4. Model providers

These can remain cloud services:

- Gemini for premium analysis and upgrades
- Hugging Face for answering or structured analysis
- OpenAI for answering if quota exists

## Native dependencies that still matter in cloud

Even with a cloud deployment, some backend routes still rely on native binaries or local runtime capabilities.

### `ffmpeg`

Needed when the backend processes video or audio.

Use cases:

- audio extraction
- video preprocessing
- future movement video analysis

### `tesseract`

Needed if OCR remains server-side.

Use cases:

- extracting visible text from frames
- enriching video evidence

### OpenCV / MediaPipe / Python CV stack

Needed for:

- image analysis
- posture measurements
- landmark extraction
- debug overlay generation

### Practical rule

If the deployed backend will handle:

- `/api/v1/chat/image-analysis`
- `/api/v1/analyze/image/rest`
- future `/api/v1/analyze/video/movement`

then the cloud environment must include the native and Python dependencies required by those routes.

## What can stay local in development

These are useful locally, but do not need to be present in the production backend by default:

- local Qdrant server
- Ollama
- local debug inspection folders
- ad hoc scripts for manual testing

## Recommended deployment shape

### Frontend

Deploy the Vite app in `D:\\chat-fisioterapia` to a static host or frontend platform.

Examples:

- Vercel
- Netlify
- Cloudflare Pages

The frontend should point to the deployed backend base URL.

Recommended target:

- `Vercel`

### Backend

Deploy the FastAPI app from `D:\\sistema-biomecanico` to a Python-capable runtime.

Examples:

- Railway
- Render
- Fly.io
- Azure App Service
- a VPS with Docker

Recommended target:

- `Railway`

### Storage and data

- Supabase stays hosted
- Qdrant Cloud stays hosted
- model providers stay hosted

## Minimum environment variables for cloud backend

At minimum, the deployed backend should have:

- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `SUPABASE_ANON_KEY`
- `QDRANT_URL`
- `QDRANT_API_KEY`
- `QDRANT_PREFER_EMBEDDED=false`
- `GEMINI_API_KEY` if Gemini is used
- `HF_TOKEN` if Hugging Face is used
- `OPENAI_API_KEY` if OpenAI is used
- storage bucket names such as:
  - `SUPABASE_CHAT_BUCKET`
  - `SUPABASE_POSTURE_BUCKET`
  - `SUPABASE_POSTURE_ANALYSIS_BUCKET`

### Production backend values to review

Before deploying, review and replace local-development values such as:

- `CORS_ALLOWED_ORIGINS`
  - remove or reduce localhost-only values
  - include the real frontend origin, e.g. `https://your-app.vercel.app`
- `QDRANT_URL`
  - should point to Qdrant Cloud, not localhost
- `OPENAI_BASE_URL`
  - should stay on the provider endpoint, not local
- `HF_ROUTER_URL`
  - should stay on the provider endpoint, not local
- `OLLAMA_BASE_URL`
  - only useful if you intentionally keep a private self-hosted Ollama instance

For production, the backend should not depend on:

- `localhost`
- `127.0.0.1`
- local file paths for public assets

## Recommended deployment order

1. Confirm Supabase migrations are applied.
2. Confirm Qdrant Cloud is populated and reachable.
3. Deploy backend with all env vars.
4. Install native dependencies in the backend runtime if image or video analysis stays server-side.
5. Verify:
   - `/api/v1/health`
   - `/api/v1/chat/models`
   - `/api/v1/chat/image-analysis`
   - `/api/v1/chat/messages`
6. Deploy the frontend and point it to the backend URL.
7. Test an authenticated end-to-end chat flow.

## Frontend environment values for cloud

The frontend should use cloud values in its `.env` or platform variables:

- `VITE_SUPABASE_URL=https://your-project.supabase.co`
- `VITE_SUPABASE_ANON_KEY=...`
- `VITE_BACKEND_URL=https://your-backend.railway.app`

The frontend should no longer point to:

- `http://127.0.0.1:8000`
- `http://localhost:8000`

except during local development.

## Supabase Auth redirects to update

When moving the frontend to the cloud, update Supabase Auth redirect URLs and site URL.

At minimum, add:

- local development URLs
  - `http://localhost:5173`
  - `http://localhost:5174`
- production frontend URL
  - `https://your-app.vercel.app`
- preview URL pattern if needed
  - `https://*.vercel.app`

Also verify:

- `Site URL` points to the production frontend
- OAuth providers such as Google and GitHub include the same callback origins

If this step is skipped, login and OAuth flows may fail even if the app deploys correctly.

## Storage and public asset URLs

The project currently uses Supabase Storage for:

- chat uploads
- posture originals
- debug overlays
- demo videos
- future-analysis public assets

That means the README, frontend, and backend should prefer:

- Supabase Storage public URLs
- or platform URLs

instead of local paths such as:

- `D:\\...`
- `/D:/...`

Local filesystem links are useful only inside the desktop workspace and should not be relied on for cloud deployment or portfolio presentation.

## Qdrant local vs cloud

### Local Qdrant

Useful for:

- development
- offline testing
- debugging collection shape
- quick rebuilds without using cloud resources

### Qdrant Cloud

Useful for:

- production retrieval
- remote backend environments
- stability and persistence
- avoiding dependence on a developer machine

If the backend is already using `QDRANT_URL` and `QDRANT_API_KEY`, Qdrant Cloud does not need any extra local process.

## Repository hygiene before deployment

Not every file under `data/knowledge` belongs in the public repository.

Recommended rule:

- keep **canonical inputs or small reference datasets**
- ignore **generated outputs** that can be reproduced from scripts

### Good candidates to keep versioned

- small reference files such as `data/knowledge/exercise_protocols.json`
- curated draft examples used as fixtures or samples
- compact registries that describe the dataset shape

### Good candidates to keep out of git

- `data/knowledge/rag_runs/*`
- bulk generated `*_level1.json`
- bulk generated `*_sync.json`
- `run_summary.json`
- scrape snapshots under `data/knowledge/youtube_channels/*`
- local Qdrant binaries and ZIP downloads

Why this matters:

- the repositories stay lightweight for portfolio and deployment
- generated artifacts do not create noisy commits
- cloning and CI remain faster
- public repos avoid carrying machine-specific tooling and temporary runs

## Buckets and debug assets

For the chat MVP with `rest_phase1`, the backend uploads:

- original images to `Postura`
- debug overlays and analysis artifacts to `Postura-analisis`

These should remain in Supabase Storage in production so the chat UI can render them remotely.

## Current practical recommendation

For the next cloud step:

- keep `Supabase` hosted
- keep `Qdrant Cloud`
- deploy the FastAPI backend to Railway
- deploy the Vite frontend to Vercel
- keep Gemini and HF as external APIs
- include `ffmpeg`, `tesseract`, and the CV stack in the backend runtime if analysis endpoints remain active there
- keep frontend and backend in separate repositories

## Related documents

- [RAG_STORAGE_SUPABASE_QDRANT.md](./RAG_STORAGE_SUPABASE_QDRANT.md)
- [RAG_TESTING_COMMANDS.md](./RAG_TESTING_COMMANDS.md)
- [CHAT_APP_BACKEND_CONTRACT.md](./CHAT_APP_BACKEND_CONTRACT.md)
- [RAG_QDRANT_LOCAL_CLOUD_AND_BATCH_41_50.md](../../data/processed/rag/RAG_QDRANT_LOCAL_CLOUD_AND_BATCH_41_50.md)
