set PROJECT=subinterpreters_v12.4
echo %date% %time%
CALL conda env create -f ../environment.yml
CALL conda activate %PROJECT%
echo %date% %time%
@REM 3 min : 15:06:55,16 - 15:10:28,21