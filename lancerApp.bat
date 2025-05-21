@echo off
title Lancement de Gestion Budgetaire UFR

:: Activer l'environnement virtuel et lancer le backend Django
start "" cmd /k "cd C:\Users\user\Desktop\GESTION_BUDGET_UFR_SET && call env_pfc\Scripts\activate && cd gestion_budgetaire_backend && python manage.py runserver"

:: Attendre quelques secondes avant de lancer le frontend
timeout /t 5 /nobreak > nul

:: Lancer le frontend compilé
start "" "C:\Users\user\Desktop\gestion_budgetaire_frontend\dist\GestionBudgetUFR.exe"

exit
