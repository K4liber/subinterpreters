set PYTHON313t_PATH="C:\Users\kamka\AppData\Local\Programs\Python\Python313\python3.13t.exe"
call %PYTHON313t_PATH% -m venv .venv313t
call .venv313t\Scripts\activate
@rem " comment out psutils library usage in runner/interface"