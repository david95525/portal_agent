# --- 1. 構建階段 ---
FROM python:3.13-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

ENV PATH="/root/.cargo/bin:${PATH}"
WORKDIR /app

# 確保編譯時使用的是 3.13
ENV UV_PYTHON=/usr/local/bin/python3.13
ENV UV_COMPILE_BYTECODE=1

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# --- 2. 運行階段 (必須與 builder 一致) ---
FROM python:3.13-slim

WORKDIR /app

# 從 builder 拷貝虛擬環境
COPY --from=builder /app/.venv /app/.venv
COPY . .

# 設定環境變數
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["python", "main.py"]
