@echo off
setlocal
pushd %~dp0\..

set PY_EXE=.venv\Scripts\python.exe
if not exist "%PY_EXE%" (
  echo Python virtual environment not found at %PY_EXE%
  echo Run: python -m venv .venv
  popd
  exit /b 1
)

"%PY_EXE%" -m uvicorn app.main:app --reload
set EXIT_CODE=%ERRORLEVEL%
popd
exit /b %EXIT_CODE%