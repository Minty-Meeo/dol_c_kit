@ECHO off
CHDIR /D "%~d0%~p0"
python setup.py install
PAUSE
