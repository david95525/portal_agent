# 1. Stop and clean up
Write-Host "--- Stopping old containers ---" -ForegroundColor Yellow
docker compose down

# 2. Build and Start
Write-Host "--- Building Agent Image (No-Cache) ---" -ForegroundColor Blue
docker compose build --no-cache portal_agent

# Check if build was successful
if ($LASTEXITCODE -ne 0) {
    Write-Host "--- Error: Build failed! ---" -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "--- Starting service ---" -ForegroundColor Green
docker compose up -d

# 3. Cleanup dangling images
Write-Host "--- Cleaning up images ---" -ForegroundColor Gray
docker image prune -f

# 4. Follow logs
Write-Host "--- Entering logs (Ctrl+C to exit) ---" -ForegroundColor Cyan
docker logs -f python_agent_service