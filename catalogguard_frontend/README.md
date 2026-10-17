# CatalogGuard frontend

A responsive React + Vite frontend for the Duplicate Product Review Queue case.

## Included

- Dashboard, review queue, product comparison, catalogue, scan history, evaluation and exports pages
- Pastel mint/lavender UI, responsive sidebar and reusable components
- Demo data and SVG product illustrations
- API service modules ready to connect to a backend
- Reviewer decisions with notes; accepting a match records the review decision only
- CSV and JSON exports in demo mode
- Evaluation view that explicitly labels demo metrics as illustrative

## Run in VS Code

1. Extract the ZIP file.
2. Open the extracted `catalogguard_frontend` folder in VS Code.
3. Open Terminal → New Terminal.
4. Ensure Node.js LTS is installed (`node -v`, `npm -v`).
5. Run:

   ```bash
   npm install
   npm run dev
   ```

6. Open the local URL Vite prints, usually `http://localhost:5173`.

## Connect your backend

Copy `.env.example` to `.env` and update:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_DEMO_MODE=false
```

Restart the Vite dev server after changing `.env`.

Expected endpoints used by the UI:

- `GET /api/products`
- `GET /api/products/:id` (optional)
- `GET /api/pairs`
- `GET /api/pairs/:id`
- `POST /api/pairs/:id/decision` with `{ "decision": "accepted|rejected|flagged", "note": "...", "reviewer": "..." }`
- `GET /api/scans`
- `POST /api/rescan`
- `GET /api/metrics`
- `GET /api/exports?format=csv|json&type=reviews|products`

Adjust `src/api/*.js` to match the backend contract if your endpoint names or response fields differ. Product records use the dataset fields `product_id`, `title`, `brand`, `model`, `pack_quantity`, and `size`; `productId` and `packQuantity` are also accepted as camelCase aliases. Optional product-detail fields such as `category`, `price`, `sku`, and `image` remain available to the comparison view. Missing text values normalize to `—`; absent or invalid pack quantities are inferred from an explicit “set/pack of N” title or default to 1. Pairs should have `id`, `leftId`, `rightId`, `score` (0–1), `status`, `reason`, and `signals`. `/api/metrics` can return `accuracy` as a percentage and optionally `accuracyCorrect` and `accuracyTotal`; when the percentage is omitted, the frontend derives it from those counts, otherwise it displays an unavailable value. False-merge cost fields (`labourMinutes`, `labourRatePerHour`, `downstreamLoss`, `remediationCost`, `falseMergeCount`, `falseMergeCostPerMerge`, and `falseMergeExposure`) are optional; missing values are calculated using `FALSE_MERGE_COST_CONFIG` and the precision counts.

## Important safety behavior

This is a suggestion-only review interface. Accepting a suggested pair must not merge, delete, overwrite, or modify catalogue products. It only records a reviewer decision. Keep the pilot in suggestion-only mode until the labelled fixture demonstrates the target precision and zero false merges of distinct variants.

The current demo values are illustrative, not measured model performance. Evaluate against `Starter_Data/C06/fixture.json` and show actual TP/FP/FN counts before making quality claims.

## Folder structure

```text
frontend/
├── public/images/
├── src/
│   ├── main.jsx
│   ├── App.jsx
│   ├── app.css
│   ├── api/
│   ├── components/
│   ├── pages/
│   ├── hooks/
│   └── utils/
├── package.json
├── vite.config.js
└── .env.example
```
