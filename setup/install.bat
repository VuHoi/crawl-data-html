@ECHO OFF
@setlocal enableextensions
@cd /d "%~dp0"
pip install xmltodict
pip install boto3
pip install python-slugify
pip install requests
pip install parsel
pause