@echo off
setlocal EnableDelayedExpansion

REM Check if .env exists
if not exist ".env" (
    echo .env file not found
    exit /b 1
)

REM Load each line in .env
for /f "usebackq delims=" %%A in (".env") do (
    REM Skip empty lines and comments
    echo %%A | findstr /R "^\s*$ ^\s*#" >nul
    if errorlevel 1 (
        set "line=%%A"
        for /f "tokens=1,* delims==" %%K in ("!line!") do (
            set "%%K=%%L"
        )
    )
)

endlocal & (
    REM Export variables to caller environment
    for /f "usebackq delims=" %%A in (".env") do (
        echo %%A | findstr /R "^\s*$ ^\s*#" >nul
        if errorlevel 1 (
            set %%A
        )
    )
)

echo Environment variables loaded from .env
