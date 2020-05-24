@echo off
python --version 
if ERRORLEVEL 1 GOTO NOPYTHON  
goto :HASPYTHON  
:NOPYTHON  
echo "doesnt have python"  
exit
:HASPYTHON  
echo "has python"
echo "checking version"
python --version 2>&1 | findstr " 2.7"
if ERRORLEVEL 1 GOTO GOODPYTHAN
goto BADPYTHON
:BADPYTHON
echo "you have the wrong version of python (you have 2.7 and we need 3.6+)"
echo "go download a new version please!"
exit
:GOODPYTHAN
echo "we are good to go!"
echo "################### INSTALLING DEPENDENCIES ###################"
python -m pip install -r requirements.txt
echo "################### RUNNING WIZRAD ###################"
python main.py
