@echo off
:loop
REM 调用 read.bat 文件
call "F:\code\python\dbhomework\read.bat"

REM 等待 3600 秒（1 小时），然后再次执行
timeout /t 3600 /nobreak >nul

REM 返回循环
goto loop