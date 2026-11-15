@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%~dp0;%PYTHONPATH%"
title AuraLife Terminal CLI - Shubhi Mathur

if exist "C:\Users\admin\Python311\python.exe" (
    set "PYCMD=C:\Users\admin\Python311\python.exe"
) else (
    set "PYCMD=python"
)

"%PYCMD%" main.py --cli
pause
