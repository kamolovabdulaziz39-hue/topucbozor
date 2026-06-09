@echo off
title GitHub Push - Top 1 UC Bozor
echo ==============================================
echo   AUTO-PUSH TO GITHUB (DEVICE CODE MODE)
echo ==============================================
echo.

echo [+] Configuring Git to use Device Code authorization...
git config --global credential.gitHubAuthModes device

echo [+] Initializing Git repository...
git init

echo [+] Adding project files...
git add .

echo [+] Creating commit...
git commit -m "Initial commit for Top 1 UC Bozor bot"

echo [+] Setting branch to main...
git branch -M main

echo [+] Configuring remote repository...
git remote remove origin
git remote add origin https://github.com/kamolovabdulaziz39-hue/-top-1-uc-bozor.git

echo.
echo ==========================================================
echo [INSTRUCTIONS]
echo Since browser launch failed, we are using DEVICE CODE mode.
echo Git will display a code (e.g. ABCD-EFGH) in this window.
echo 1. Open this website in your browser: https://github.com/login/device
echo 2. Type the code shown in the terminal.
echo ==========================================================
echo.
pause

git push -u origin main

echo.
echo ==============================================
echo [FINISHED] Done! You can close this window.
echo ==============================================
pause
