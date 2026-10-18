# Catalogue-AI
A duplicate product listing review system that suggests potential duplicates using matching evidence, protects distinct product variants from false merges, and supports reviewer decisions and CSV/JSON exports. Includes validation, testing, catalogue operations design, and a business pilot plan.

## Deploy to Render

The root `render.yaml` defines a single Docker-based web service. Render builds the
Vite frontend and serves it with the FastAPI backend, so frontend API requests and
authentication cookies use the same origin. Create a Blueprint in Render from this
GitHub repository and deploy the `main` branch.

The Blueprint uses Render's free plan and SQLite at `/tmp/review.db`. That filesystem
is ephemeral: review decisions and accounts may be lost when the service restarts or
is redeployed. Use a persistent storage option before relying on this deployment for
long-lived or production data.

The deployed frontend runs with `VITE_DEMO_MODE=false`. The backend's health endpoint
is available at `/health`.
