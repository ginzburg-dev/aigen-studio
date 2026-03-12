# Pipeline Builder Deployment Guide

This guide covers release, deployment, workstation rollout, environment setup, and rollback.

## 1) Decide Deployment Topology

Use one of these:

1. Centralized API + centralized web app (recommended for teams).
2. Local Docker stack on each workstation.
3. Local Node processes on each workstation (no Docker).

Recommended: centralized hosting to avoid drift and simplify upgrades.

## 2) Environments

Use `.env` files per environment.

Required for app itself:
- `HOST` (backend bind host, usually `0.0.0.0`)
- `PORT` (backend bind port, default `3001`)
- `FRONTEND_PORT` (compose host port, default `8080`)
- `BACKEND_PORT` (compose host port, default `3001`)

If your pipeline runner executes GPT actions:
- `OPENAI_API_KEY`
- `CONFIGS_ROOT_DIR` (optional)
- `AIGEN_CACHE_DIR` (optional)

Template: `.env.example`.

## 3) Release Process

1. Prepare release branch.
2. Validate build locally:
```bash
cd /Users/dmitryginzburg/Development/aigen-studio/pipeline-builder
npm ci
npm run typecheck
npm run build
```
3. Tag release:
```bash
git tag pipeline-builder-v0.1.0
git push origin pipeline-builder-v0.1.0
```
4. CI builds and validates Node workspace.
5. Release workflow builds/pushes Docker images.
6. Deploy tagged images to target environment.

## 4) Docker Deployment (Server or Workstation)

1. Copy `.env.example` to `.env` and fill values.
2. Start stack:
```bash
cd /Users/dmitryginzburg/Development/aigen-studio/pipeline-builder
docker compose up -d --build
```
3. Verify:
- Frontend: `http://<host>:${FRONTEND_PORT}`
- Backend health: `http://<host>:${BACKEND_PORT}/health`

Compose services:
- `frontend`: Nginx serving SPA and proxying `/api/*` to backend.
- `backend`: Fastify API service.

## 5) Non-Docker Deployment (Workstation)

1. Install Node 22+.
2. Install and build:
```bash
cd /Users/dmitryginzburg/Development/aigen-studio/pipeline-builder
npm ci
npm run build
```
3. Run backend:
```bash
HOST=127.0.0.1 PORT=3001 node --import tsx apps/backend/dist/index.js
```
4. Run frontend (dev mode) or serve built files from `apps/frontend/dist`.

## 5.1) One Command Workstation UX

Install launcher once:

```bash
cd /Users/dmitryginzburg/Development/aigen-studio/pipeline-builder
npm run install:command
```

Use command:

```bash
pipeline-builder up
pipeline-builder status
pipeline-builder logs
pipeline-builder down
```

## 6) Rollback

1. Pick previous stable tag/image.
2. Redeploy previous image versions.
3. Confirm `/health` and basic UI operations.

For local non-Docker rollback:
```bash
git checkout <previous-tag>
npm ci
npm run build
```

## 7) Operational Checklist

1. Restrict CORS to known origins before internet exposure.
2. Put HTTPS reverse proxy in front of frontend/backend.
3. Centralize logs and keep a simple uptime check for `/health`.
4. Keep release tags immutable and documented.

## 8) CI/CD Workflows in This Repo

- `python-tests.yaml`: existing Python tests.
- `pipeline-builder-ci.yaml`: Node CI for pipeline-builder.
- `pipeline-builder-release.yaml`: Docker image build/push on `pipeline-builder-v*` tags or manual trigger.
