# Pipeline Builder (Node Monorepo)

Node-based pipeline editor with:
- React Flow frontend for graph editing
- Fastify backend for validation and compilation
- Shared schema package for node definitions, graph validation, and instruction generation

## Workspace Structure

- `apps/frontend`: React + TypeScript + React Flow UI
- `apps/backend`: Fastify + TypeScript API
- `packages/schema`: shared graph types, node catalog, `validateGraph`, `compileGraph`

## Quick Start

```bash
cd pipeline-builder
npm install
```

Run backend (port `3001`):

```bash
npm run dev:backend
```

Run frontend (port `5173`):

```bash
npm run dev:frontend
```

Frontend talks to `http://localhost:3001` by default.
Override with:

```bash
VITE_API_BASE_URL=http://localhost:3001
```

## Backend API

- `GET /health`
- `GET /node-definitions`
- `POST /validate` with `{ nodes, edges }`
- `POST /compile` with `{ nodes, edges }` -> returns validation + compiled Aigen instructions

## Implemented Nodes (all Aigen nodes)

- `SetVariable`
- `CopyVariable`
- `ReadFile`
- `WriteFile`
- `PrintVariable`
- `GPTChat`
- `ParseJSON`
- `JsonToContext`
- `ReplaceBetween`
- `ResolveTemplateVars`

## Compile Output Shape

```json
{
  "format": "aigen.instructions.v1",
  "generatedAt": "2026-03-11T12:00:00.000Z",
  "instructions": [
    {
      "node": "SetVariable",
      "params": { "name": "prompt_step_1", "value": "Describe each image in exactly 10 words." }
    },
    {
      "node": "GPTChat",
      "params": {
        "model": "gpt-4o-mini",
        "prompt": [{ "type": "text", "content": "prompt_step_1" }],
        "output": "image_description"
      }
    }
  ]
}
```

## Notes

- Graphs are validated as DAGs; cycles fail compilation.
- Input port type compatibility is checked both in UI and backend.
- Save exports runtime-compatible YAML/JSON instruction lists (`- node: ...`).
- Load YAML reconstructs graph nodes and edges from instruction steps.

## Deployment

- Deployment runbook: `DEPLOYMENT.md`
- Docker stack: `docker-compose.yml`
- Backend image build: `Dockerfile.backend`
- Frontend image build: `Dockerfile.frontend`
- Env template: `.env.example`

## One Command Launcher

Install local `pipeline-builder` command:

```bash
cd /Users/dmitryginzburg/Development/aigen-studio/pipeline-builder
npm run install:command
```

Then use:

```bash
pipeline-builder up
pipeline-builder status
pipeline-builder logs
pipeline-builder down
```
