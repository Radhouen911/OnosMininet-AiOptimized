@echo off
REM Script de démarrage automatique pour Windows

echo ==========================================
echo Demarrage de l'environnement ONOS + Mininet + RAVEN
echo ==========================================
echo.

echo 1. Demarrage des conteneurs...
docker compose up -d

echo.
echo 2. Attente du demarrage d'ONOS (90 secondes)...
timeout /t 90 /nobreak > nul

echo.
echo 3. Verification qu'ONOS est pret...
curl -s -u onos:rocks http://localhost:8181/onos/v1/applications > nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] ONOS est pret!
) else (
    echo [ATTENTION] ONOS n'est pas encore pret, attendez encore 30 secondes...
    timeout /t 30 /nobreak > nul
)

echo.
echo ==========================================
echo Environnement pret!
echo ==========================================
echo.
echo Acces:
echo   - GUI ONOS:  http://localhost:8181/onos/ui/index.html
echo   - Login:     onos / rocks
echo   - API REST:  http://localhost:8181/onos/v1/
echo.
echo Pour lancer la topologie Diamond4:
echo   docker exec -it mininet bash
echo   mn --custom /topologies/diamond4.py --topo diamond4 --controller remote,ip=onos,port=6653
echo.
echo Logs RAVEN:
echo   docker logs -f raven-controller
echo.
echo ==========================================
pause
