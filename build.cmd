pip install Flask pyinstaller pywin32
pyinstaller --onefile --noconsole --icon="cp.ico" --hidden-import="jinja2" --hidden-import="werkzeug" --name=cp cp.py
pyinstaller --onefile --windowed --icon="copyaz.ico" --name "CopyAZ" --hidden-import "win32timezone" CopyAZ.py