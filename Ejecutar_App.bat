@echo off
echo Iniciando el Banco de Ajustes Razonables (I.PS.I.)...
echo Por favor, no cierres esta ventana mientras uses la aplicacion.
call "%~dp0.venv\Scripts\python.exe" -m streamlit run "%~dp0app.py"
pause
