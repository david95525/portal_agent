# BP AI Agent Service

基於 FastAPI 與 LangGraph 構建的血壓數據助理服務，具備意圖識別、數據查詢、統計計算與對話狀態持久化功能。

## 核心功能
*   **智能路由**：自動判斷用戶意圖（查詢紀錄、數據統計、一般寒暄）。
*   **數據整合**：串接外部 API 獲取用戶血壓歷史數據。
*   **數據統計**：針對血壓數據提供精確的統計結果（如平均值、高血壓頻率、最大最小值等），不提供醫學建議。
*   **狀態持久化**：使用 SQLite 紀錄對話上下文，即使重啟服務也能延續對話。

## 技術棧
*   **框架**: [FastAPI](https://fastapi.tiangolo.com/)
*   **AI 工作流**: [LangGraph](https://langchain-ai.github.io/langgraph/) / [LangChain](https://www.langchain.com/)
*   **環境管理**: [uv](https://github.com/astral-sh/uv)
*   **容器化**: Docker & Docker Compose

## 快速開始

### 1. 環境設定
複製 `.env.example` 並填入您的 API Key：
```bash
cp .env.example .env
```
主要變數：
* `GEMINI_API_KEY`: Google Gemini API 密鑰
* `API_DOMAIN`: 外部血壓數據 API 的網域

### 2. 使用 Docker 啟動 (推薦)
```bash
docker-compose up --build -d
```
服務將運行在 `http://localhost:8000`。

### 3. 本地開發
安裝相依性：
```bash
uv sync
```
啟動服務：
```bash
python main.py
```

## API 說明
*   **POST `/api/v1/bp/chat`**: 與 AI 助理對話。
    *   `user_id`: 用戶唯一識別碼。
    *   `message`: 用戶輸入內容。
    *   `user_token`: 用於查詢數據 API 的身份憑證。
*   **GET `/demo`**: 簡易測試前端介面。

## 專案結構
*   `app/api/`: API 路由定義。
*   `app/services/bp_agent/`: LangGraph 狀態機與節點邏輯。
*   `app/core/`: 系統配置管理。
*   `static/`: 前端展示檔案。
*   `data/`: SQLite 資料庫持久化目錄。
