#!/bin/bash

# Git Account Switcher Script

echo "Select Git account to use:"
echo "1) tushar-kumar-9354 (tushar)"
echo "2) yashsilotia1 (yash)"
echo "3) Show current config"
echo "4) Exit"

read -p "Enter choice (1-4): " choice

case $choice in
    1)
        echo "Switching to tushar-kumar-9354 account..."
        
        # Update git config for this repository
        git config user.name "tushar-kumar-9354"
        git config user.email "tushar@github.com"  # Replace with your actual email
        
        # Change remote origin to use tushar SSH host
        git remote set-url origin git@github.com-tushar:tushar-kumar-9354/pankaj-.git
        
        echo "✓ Switched to tushar-kumar-9354 account"
        echo "Remote URL updated to: https://github.com/tushar-kumar-9354/pankaj-"
        ;;
    2)
        echo "Switching to yashsilotia1 account..."
        
        # Update git config for this repository
        git config user.name "yashsilotia1"
        git config user.email "yash@github.com"  # Replace with your actual email
        
        # Change remote origin to use yash SSH host
        git remote set-url origin git@github.com-yash:yashsilotia1/PANKAJ.git
        
        echo "✓ Switched to yashsilotia1 account"
        echo "Remote URL updated to: https://github.com/yashsilotia1/PANKAJ"
        ;;
    3)
        echo "Current Git configuration:"
        echo "-------------------------"
        echo "Username: $(git config user.name)"
        echo "Email: $(git config user.email)"
        echo "Remote URL: $(git remote get-url origin)"
        echo "-------------------------"
        ;;
    4)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid choice!"
        exit 1
        ;;
esac