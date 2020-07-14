@echo off
rem --- 
rem ---  exeを生成
rem --- 

rem ---  カレントディレクトリを実行先に変更
cd /d %~dp0

cls

activate pytest_release && pyinstaller --clean pytest64.spec
