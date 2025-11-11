@echo off
REM ========================================
REM  INSTALADOR AUTOMATICO - FGTS ROBOT
REM ========================================
REM
REM Duplo clique neste arquivo para instalar tudo!
REM

echo.
echo ========================================
echo  INSTALADOR AUTOMATICO
echo  FGTS Digital Robot
echo ========================================
echo.
echo Este programa vai instalar tudo automaticamente.
echo.
echo Pode demorar alguns minutos...
echo.
pause

echo.
echo Iniciando instalacao...
echo.

REM Executar script Python de instalação
python instalar_playwright.py

echo.
echo ========================================
echo  PRONTO!
echo ========================================
echo.
echo Agora voce pode executar o programa:
echo.
echo 1. Duplo clique em: run_fgts_robot.py
echo    ou
echo 2. Execute: python run_fgts_robot.py
echo.
pause
