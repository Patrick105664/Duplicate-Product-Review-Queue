FROM node:22-alpine AS frontend-build

WORKDIR /app/catalogguard_frontend
COPY catalogguard_frontend/package*.json ./
RUN npm ci
COPY catalogguard_frontend/ ./
ENV VITE_DEMO_MODE=false
ENV VITE_API_BASE_URL=
RUN npm run build

FROM python:3.12-slim

WORKDIR /app
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt
COPY backend/ ./backend/
COPY C06_Duplicate_Review/ ./C06_Duplicate_Review/
COPY --from=frontend-build /app/catalogguard_frontend/dist ./catalogguard_frontend/dist

ENV REVIEW_DB_PATH=/tmp/review.db
ENV SERVE_FRONTEND=true
EXPOSE 10000

CMD ["sh", "-c", "uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port ${PORT:-10000}"]
