@echo off
setlocal
pushd %~dp0\..

set PY_EXE=.venv\Scripts\python.exe
if not exist "%PY_EXE%" (
  echo Python virtual environment not found at %PY_EXE%
  popd
  exit /b 1
)

"%PY_EXE%" scripts\reload_server.py
set EXIT_CODE=%ERRORLEVEL%
popd
exit /b %EXIT_CODE%