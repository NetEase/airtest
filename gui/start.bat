@echo off
set PYTHONPATH="z:/workspace/airtest"
cmd /c "pyuic4.bat mainui.ui -o mainui.py"
python main.py