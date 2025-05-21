@echo off
:: Activer l'environnement virtuel
call env_pyqt\Scripts\activate

echo [*] Suppression des anciens builds...
rmdir /s /q dist
rmdir /s /q build
del /q *.spec

echo [*] Construction de l'exécutable avec PyInstaller...
pyinstaller ^
 --noconfirm ^
 --onefile ^
 --name "GestionBudgetUFR" ^
 --windowed ^
 --icon=ufr.ico ^
 --add-data "assets;assets" ^
 --add-data "services;services" ^
 --add-data "modules;modules" ^
 --add-data "ui;ui" ^
 --add-data "config.py;." ^
 main.py

echo [✔] Terminé. Exécutable généré dans le dossier "dist\".
pause
