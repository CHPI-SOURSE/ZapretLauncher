@echo off
cd /d "%~dp0"
powershell -Command "Start-Process 'pythonw.exe' -ArgumentList 'launcher.py' -Verb RunAs"