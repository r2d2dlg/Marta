@echo off
REM Script para lanzar la aplicación web de Marta AI

REM --- Configuración (AJUSTA ESTA RUTA SI ES NECESARIO) ---
REM Ruta completa a la carpeta raíz de tu proyecto Marta AI
set PROJECT_DIR=F:\projects\marta_ai
REM Nombre de la carpeta de tu entorno virtual
set VENV_DIR=venv
REM Nombre del script principal de la aplicación Flask
set FLASK_APP_SCRIPT=webapp.py
REM Puerto en el que corre la aplicación Flask (debe coincidir con webapp.py)
set FLASK_PORT=5001

REM --- Fin de Configuración ---

echo Iniciando la aplicacion web de Marta AI...

REM Cambiar al directorio del proyecto
cd /d "%PROJECT_DIR%"
if errorlevel 1 (
    echo ERROR: No se pudo cambiar al directorio del proyecto: %PROJECT_DIR%
    pause
    exit /b 1
)

REM Activar el entorno virtual
echo Activando entorno virtual...
call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    echo ERROR: No se pudo activar el entorno virtual en %PROJECT_DIR%\%VENV_DIR%
    echo Asegurate de que el entorno virtual exista y la ruta sea correcta.
    pause
    exit /b 1
)

REM Iniciar la aplicación Flask
echo Iniciando servidor Flask (webapp.py)...
REM El comando start /B permite que el script continúe y abra el navegador
REM sin esperar a que el servidor Flask termine (ya que es un servidor persistente).
start "Marta WebApp Server" /B python "%FLASK_APP_SCRIPT%"

REM Esperar unos segundos para que el servidor Flask inicie
echo Esperando a que el servidor inicie (5 segundos)...
timeout /t 5 /nobreak > nul

REM Abrir la aplicación en el navegador por defecto
echo Abriendo Marta AI en tu navegador...
start http://localhost:%FLASK_PORT%/

echo.
echo La aplicacion de Marta AI deberia estar corriendo y abriendose en tu navegador.
echo Puedes cerrar esta ventana de comandos, pero el servidor de Marta (otra ventana de comandos)
echo debe permanecer abierto para que la aplicacion web funcione.

REM Si quieres que esta ventana se cierre automáticamente después de un tiempo,
REM puedes descomentar la siguiente línea (ej. cerrar después de 10 segundos)
REM timeout /t 10 /nobreak > nul
REM exit /b 0

REM Si prefieres que esta ventana se quede abierta para ver mensajes, déjala así o añade 'pause'
pause
