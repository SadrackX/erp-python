@echo off
echo Ativando ambiente virtual...
call .\.venv\Scripts\activate.bat

echo Iniciando servidor Flask...
python run.py

pause
