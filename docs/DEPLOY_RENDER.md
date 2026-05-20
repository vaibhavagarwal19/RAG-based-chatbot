# Deploy on Render

This guide deploys the RAG chatbot as a **Docker Web Service** on [Render](https://render.com).

## Requirements

| Item | Notes |
|------|--------|
| **Render account** | [render.com](https://render.com) |
| **Groq API key** | [console.groq.com](https://console.groq.com/keys) |
| **Git repo** | Push this project to GitHub/GitLab |
| **Plan** | **Starter ($7/mo)** or higher recommended — Free tier (512MB RAM) often fails during embedding model load |

## Option A — Blueprint (fastest)

1. Push the project to GitHub.
2. In Render: **New +** → **Blueprint**.
3. Connect the repository and apply `render.yaml`.
4. When prompted, set **`GROQ_API_KEY`** (mark as secret).
5. Wait for the Docker build (10–20 minutes first time).
6. Open the service URL (e.g. `https://rag-chatbot-xxxx.onrender.com`).

The blueprint mounts a **1GB persistent disk** at `/app/data` so the FAISS index survives restarts.

## Option B — Manual setup

1. **New +** → **Web Service** → connect your repo.
2. Settings:
   - **Language:** Docker
   - **Dockerfile path:** `./Dockerfile`
   - **Plan:** Starter (or higher)
   - **Health check path:** `/health`
3. **Environment** → add variables:
   - `GROQ_API_KEY` = your key (secret)
   - `GROQ_MODEL` = `llama-3.3-70b-versatile` (optional)
4. **Disks** → Add disk:
   - **Mount path:** `/app/data`
   - **Size:** 1 GB
5. **Create Web Service** and wait for deploy.

## After deploy

1. Open `https://<your-service>.onrender.com/`
2. Check indexing: `https://<your-service>.onrender.com/status`  
   - `"ready": true` when the vector index is built
3. Upload a PDF in the UI or copy a file into the disk via shell (advanced).

### First startup

- The service starts immediately; **PDF indexing runs in the background**.
- Large PDFs can take **several minutes** on CPU before chat works.
- Put PDFs in the repo under `data/uploads/` **before** deploy, or upload via the UI after deploy (files land on the persistent disk).

## Rebuild index on Render

If you change ingestion code or PDFs, delete the index and restart:

1. **Shell** tab in Render dashboard (if available on your plan), or redeploy after removing index files.
2. From shell:
   ```bash
   rm -rf /app/data/faiss_index
   ```
3. **Manual Deploy** → **Clear build cache & deploy** (or restart service) to trigger a fresh index build.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Build fails / out of memory | Upgrade to **Starter** or higher |
| Service crashes on startup | Check **Logs**; confirm `GROQ_API_KEY` is set |
| `Invalid API Key` in chat | Fix `GROQ_API_KEY` in Environment, redeploy |
| Index never becomes ready | Large PDF + CPU; wait longer; check logs for `FAISS index ready` |
| Slow cold start | Render free/starter spins down after inactivity; first request wakes the service |
| Data lost after deploy | Attach a **disk** mounted at `/app/data` (see above) |

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | Yes | Groq API key |
| `GROQ_MODEL` | No | Default `llama-3.3-70b-versatile` |
| `PORT` | Auto | Set by Render; used by `scripts/start.sh` |
| `SKIP_INDEX_BUILD` | No | Set `1` only for tests |

## Custom domain (optional)

Render dashboard → your service → **Settings** → **Custom Domains**.
