
# C:/Python310/python.exe -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r .\requirements.txt

./compileUi.ps1

pip3 install --upgrade PyInstaller pyinstaller-hooks-contrib
pyinstaller.exe .\SoundKey2.py