# ┌─────────────────────────────┐
# │   Stage 1: Build Frontend   │
# └─────────────────────────────┘
FROM node:18-alpine AS frontend-build

WORKDIR /app/frontend

COPY frontend/package*.json ./  
COPY frontend/yarn.lock     ./  
RUN yarn install --frozen-lockfile

COPY frontend/ .  
RUN yarn build    # produces /app/frontend/dist


# ┌─────────────────────────────┐
# │   Stage 2: Build Backend    │
# └─────────────────────────────┘
FROM python:3.12-slim AS backend-build

WORKDIR /app

# install Python deps into a venv
COPY backend/requirements.txt .  
RUN python -m venv venv \
 && . venv/bin/activate \
 && pip install --no-cache-dir -r requirements.txt

# copy backend source
COPY backend/ .

# copy the built frontend into static/
COPY --from=frontend-build /app/frontend/dist ./static

EXPOSE 8000

CMD ["venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]
