# PowerShell script to push scratch repository to https://github.com/Abhinandan9508/langgraph-agentic-voice-support.git

Write-Host "Updating remote URL to https://github.com/Abhinandan9508/langgraph-agentic-voice-support.git..." -ForegroundColor Green
git remote set-url origin https://github.com/Abhinandan9508/langgraph-agentic-voice-support.git

Write-Host "Switching to main branch..." -ForegroundColor Green
git checkout -B main

Write-Host "Staging all project files..." -ForegroundColor Green
git add .

Write-Host "Committing project files..." -ForegroundColor Green
git commit -m "feat: initial commit of complete LangGraph agentic voice support project"

Write-Host "Pushing all project files to GitHub..." -ForegroundColor Green
git push -u origin main

Write-Host "`nProject successfully pushed to GitHub repository:" -ForegroundColor Cyan
Write-Host "https://github.com/Abhinandan9508/langgraph-agentic-voice-support" -ForegroundColor Yellow
