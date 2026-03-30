import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.bp_router import router as bp_router, bp_service
from app.utils.logger import setup_logger

logger = setup_logger("MainApp")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info("Initializing BP Agent Service...")
    await bp_service.initialize()
    yield
    # Shutdown logic
    logger.info("Shutting down BP Agent Service...")
    await bp_service.close()

app = FastAPI(title="AI Agent Service", lifespan=lifespan)

# 設定 CORS 密鑰 (Middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允許所有來源 (開發環境可設為 *, 生產環境建議設具體來源)
    allow_credentials=True,
    allow_methods=["*"],  # 允許所有 HTTP 方法 (GET, POST, OPTIONS, 等)
    allow_headers=["*"],  # 允許所有標頭
)

# 註冊路由
app.include_router(bp_router, prefix="/api/v1/bp", tags=["Blood Pressure"])

# 掛載靜態檔案 (供 CSS/JS 引用)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def index():
    return {"message": "Welcome to BP AI Agent Service"}

@app.get("/demo")
async def demo():
    return FileResponse("static/demo.html")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
