@echo off
echo Running Your Python Script...
call .\WPy64-31160\python-3.11.6.amd64\python.exe ballots.py
echo Deactivating environment...

REM pip install sys asyncio aiohttp json requests shutil pdf2docx PyQt5 PyQtWebEngine jinja2 datetime re pyppeteer pillow collections