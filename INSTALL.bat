@ECHO off
CHDIR /D "%~d0%~p0"
pip install pyelftools --upgrade
pip install dolreader --upgrade
pip install geckolibs --upgrade
python setup.py install
PAUSE
