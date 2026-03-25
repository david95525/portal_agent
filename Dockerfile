# --- 構建阶段 ---
FROM python:3.13-slim AS builder

# 安裝 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 【修改】安装编译 Pydantic/Rust 依賴所需的工具
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

#  Rust 加入環境
ENV PATH="/root/.cargo/bin:${PATH}"

WORKDIR /app

ENV UV_PYTHON=/usr/local/bin/python3.13

ENV UV_COMPILE_BYTECODE=1
# 複製依赖文件同步
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# --- 運行 ---
FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY . .

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["python", "main.py"]
