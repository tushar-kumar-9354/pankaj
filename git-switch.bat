@echo off
echo Git Account Switcher
echo ===================
echo 1) tushar-kumar-9354 (tushar)
echo 2) yashsilotia1 (yash)
echo 3) Show current config
echo 4) Exit
echo.

set /p choice="Enter choice (1-4): "

if "%choice%"=="1" (
    echo Switching to tushar-kumar-9354 account...
    git config user.name "tushar-kumar-9354"
    git config user.email "tushar@github.com"
    git remote set-url origin git@github.com-tushar:tushar-kumar-9354/pankaj-.git
    echo ✓ Switched to tushar-kumar-9354 account
    echo Remote URL updated to: https://github.com/tushar-kumar-9354/pankaj-
) else if "%choice%"=="2" (
    echo Switching to yashsilotia1 account...
    git config user.name "yashsilotia1"
    git config user.email "yash@github.com"
    git remote set-url origin git@github.com-yash:yashsilotia1/PANKAJ.git
    echo ✓ Switched to yashsilotia1 account
    echo Remote URL updated to: https://github.com/yashsilotia1/PANKAJ
) else if "%choice%"=="3" (
    echo Current Git configuration:
    echo -------------------------
    for /f "delims=" %%a in ('git config user.name') do echo Username: %%a
    for /f "delims=" %%a in ('git config user.email') do echo Email: %%a
    for /f "delims=" %%a in ('git remote get-url origin') do echo Remote URL: %%a
    echo -------------------------
) else if "%choice%"=="4" (
    echo Exiting...
    exit /b 0
) else (
    echo Invalid choice!
    exit /b 1
)
pause