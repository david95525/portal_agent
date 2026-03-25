import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.bp_router import router as bp_router
from app.utils.logger import setup_logger

logger = setup_logger("MainApp")
app = FastAPI(title="AI Agent Service")

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
