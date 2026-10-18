# Catalogue-AI
A duplicate product listing review system that suggests potential duplicates using matching evidence, protects distinct product variants from false merges, and supports reviewer decisions and CSV/JSON exports. Includes validation, testing, catalogue operations design, and a business pilot plan.

## Deploy to Vercel and Render

Deploy the Vite frontend and FastAPI backend as separate services:

1. In Vercel, import this GitHub repository and set the project root to
   `catalogguard_frontend`. The frontend `vercel.json` configures the Vite build,
   `dist` output, and client-side route fallback.
2. Add these Vercel environment variables for Production (and Preview if needed):
   - `VITE_API_BASE_URL`: the Render API origin, for example
     `https://duplicate-product-review-queue.onrender.com` (no trailing slash).
   - `VITE_DEMO_MODE`: `false`.
3. In Render, create or sync a Blueprint from the repository's root `render.yaml`.
   It deploys the API-only Docker service and exposes `/health`.
4. Set Render's `CORS_ORIGINS` environment variable to the exact Vercel site origin,
   such as `https://your-project.vercel.app`. Include any custom frontend domains as
   comma-separated origins, without paths or trailing slashes.

The Render service configures secure cross-site session cookies for the separately
hosted frontend. It uses SQLite at `/tmp/review.db` on the free plan; this storage is
ephemeral, so accounts and review data may be lost after restarts or redeployments.
Use persistent storage before relying on the deployment for long-lived data.
