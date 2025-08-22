@setlocal
@echo off
set PYTHON=%UserProfile%\AppData\Local\Programs\Python\Python310\python.exe
IF NOT EXIST venv ( %PYTHON% -m venv venv )
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
IF NOT EXIST requirements.txt ( touch requirements.txt )
pip install -r requirements.txt
cmd /k
@endlocal
