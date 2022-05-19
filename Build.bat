cd /d %~dp0
setlocal
python -X utf8 Build.py
set /p waiting=""
endlocal
exit /b 0
