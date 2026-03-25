# --- 构建阶段 ---
FROM python:3.12-slim AS builder

# 安装 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 【修改】安装编译 Pydantic/Rust 依赖所需的工具
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# 将 Rust 加入环境变量
ENV PATH="/root/.cargo/bin:${PATH}"

WORKDIR /app

# 启用字节码预编译，加快启动速度
ENV UV_COMPILE_BYTECODE=1

# 复制依赖文件并同步
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# --- 运行阶段 ---
FROM python:3.12-slim

WORKDIR /app

# 从 builder 拷贝虚拟环境（运行阶段不需要安装 Rust，镜像依然很小）
COPY --from=builder /app/.venv /app/.venv
COPY . .

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["python", "main.py"]
