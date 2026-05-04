@echo off
echo AI_ORQ_2BRAIN — Iniciando...
echo.

cd /d "%~dp0"

where python >nul 2>&1 || (echo Python nao encontrado. Instale Python 3.11+ && pause && exit /b 1)

if not exist ".venv" (
  echo Criando ambiente virtual...
  python -m venv .venv
)

call .venv\Scripts\activate.bat

echo Instalando dependencias...
pip install -r requirements.txt -q

echo.
echo Servidor a iniciar em http://localhost:8000
echo Dashboard: http://localhost:8000
echo API Docs:  http://localhost:8000/docs
echo.
start "" http://localhost:8000

python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

pause
