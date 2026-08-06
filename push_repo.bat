@echo off
echo ========================================================
echo Pushing project to https://github.com/Abhinandan9508/langgraph-agentic-voice-support.git
echo ========================================================

cd /d "%~dp0"

echo [1/4] Setting remote URL...
git remote set-url origin https://github.com/Abhinandan9508/langgraph-agentic-voice-support.git

echo [2/4] Switching to main branch...
git checkout -B main

echo [3/4] Staging all files...
git add .
git commit -m "feat: initial commit of complete LangGraph agentic voice support project"

echo [4/4] Pushing to GitHub...
git push -u origin main

echo.
echo ========================================================
echo SUCCESS! Project pushed to GitHub.
echo Repository: https://github.com/Abhinandan9508/langgraph-agentic-voice-support
echo ========================================================
pause
