@echo off
REM ========================================
REM  CRIAR EXECUTAVEL - FGTS ROBOT
REM ========================================
REM
REM Cria um arquivo .exe que funciona sem Python
REM

echo.
echo ========================================
echo  CRIAR EXECUTAVEL (.exe)
echo  FGTS Digital Robot
echo ========================================
echo.
echo Este processo vai criar um arquivo .exe que:
echo.
echo  - Funciona SEM precisar instalar Python
echo  - Pode ser copiado para qualquer computador
echo  - Abre com duplo clique
echo.
echo ATENCAO:
echo  - Tamanho final: ~300-500 MB
echo  - Tempo: 10-20 minutos
echo  - Precisa de internet
echo.
pause

echo.
echo Iniciando criacao do executavel...
echo.

REM Executar script Python
python criar_executavel.py

echo.
pause
