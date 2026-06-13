@echo off
echo Activating YakSync virtual environment...
call venv\Scripts\activate.bat
echo.
echo Environment activated!
echo Python version:
python --version
echo Django version:
python -m django --version
echo.
echo To run the development server:
echo python manage.py runserver
