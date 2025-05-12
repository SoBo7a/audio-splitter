# ┌─────────────────────────────┐
# │   Stage 1: Build Frontend   │
# └─────────────────────────────┘
FROM node:18-alpine AS frontend-build

WORKDIR /app/frontend

# copy only the lock-and-manifest so we can cache installs
COPY frontend/package.json frontend/package-lock.json ./

# install with npm (instead of yarn)
RUN npm ci

# bring in the rest of your source & build
COPY frontend/ .
RUN npm run build    # produces dist/

# ┌─────────────────────────────┐
# │   Stage 2: Build Backend    │
# └─────────────────────────────┘
FROM python:3.12-slim AS backend-build

WORKDIR /app

# 1) Install ffmpeg (and any other system deps)
RUN apt-get update \
 && apt-get install -y --no-install-recommends ffmpeg \
 && rm -rf /var/lib/apt/lists/*

# 2) Install backend deps
COPY backend/requirements.txt .
RUN python -m venv venv \
 && . venv/bin/activate \
 && pip install --no-cache-dir -r requirements.txt

# 3) Copy backend code
COPY backend/ .

# 4) Copy built frontend into ./static
COPY --from=frontend-build /app/frontend/dist ./static

EXPOSE 8000
CMD ["venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]
