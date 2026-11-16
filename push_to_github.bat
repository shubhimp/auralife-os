@echo off
title Push AuraLife OS to GitHub
echo ========================================================
echo   AuraLife OS - Quick GitHub Publisher
echo   Author: Shubhi Mathur
echo ========================================================
echo.
echo Make sure you have created an empty repository on GitHub:
echo https://github.com/new
echo.
set /p REPO_URL="Enter your GitHub Repository URL (e.g., https://github.com/username/repo.git): "

if "%REPO_URL%"=="" (
    echo [ERROR] No URL provided. Aborting.
    pause
    exit /b 1
)

echo.
echo [1/3] Checking Git status...
git remote remove origin 2>nul
echo [2/3] Adding remote origin: %REPO_URL%
git remote add origin %REPO_URL%
echo [3/3] Pushing main branch to GitHub...
git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================================
    echo   [SUCCESS] Successfully pushed to GitHub!
    echo   View your repo at: %REPO_URL%
    echo ========================================================
) else (
    echo.
    echo [NOTE] If this is your first time, GitHub may ask you to sign in.
    echo Please follow the on-screen prompt to authenticate.
)

pause
