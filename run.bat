@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%~dp0;%PYTHONPATH%"
title AuraLife - Shubhi Mathur's Command Center

if exist "C:\Users\admin\Python311\python.exe" (
    set "PYCMD=C:\Users\admin\Python311\python.exe"
) else (
    set "PYCMD=python"
)

echo =================================================================
echo   Starting AuraLife Command Center...
echo   Created by Shubhi Mathur
echo =================================================================

"%PYCMD%" main.py
pause
