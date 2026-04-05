@echo off
cd /d "%~dp0"
python -c "from lightrag.api.lightrag_server import main; main()"
