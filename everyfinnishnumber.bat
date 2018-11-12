set PYTHON=C:\Python27\python.exe
set DROPBOX_BIN=E:\Users\hugovk\Dropbox\bin
set DROPBOX_DATA=E:\Users\hugovk\Dropbox\bin\data
set TEE=%DROPBOX_BIN%\UnxUtils\tee

:loop

@date/t && time/t
@%PYTHON% %DROPBOX_BIN%\everyfinnishno.py -nw
@date/t && time/t

@%PYTHON% %DROPBOX_BIN%\sleep.py 60 REM 1 mins (sleep.exe not on all WinXP)

goto loop
