#!/bin/bash
# Setup GitHub SSH authentication

echo "🔐 Setting up GitHub SSH authentication..."
echo ""

# Check if SSH key already exists
if [ -f ~/.ssh/id_rsa ]; then
    echo "SSH key already exists. Using existing key."
else
    echo "Generating new SSH key..."
    ssh-keygen -t rsa -b 4096 -C "your-email@example.com" -f ~/.ssh/id_rsa -N ""
fi

echo ""
echo "📋 Copy this SSH public key to GitHub:"
echo "=================================="
cat ~/.ssh/id_rsa.pub
echo "=================================="
echo ""
echo "Steps to add to GitHub:"
echo "1. Go to https://github.com/settings/keys"
echo "2. Click 'New SSH key'"
echo "3. Give it a title (e.g., 'CECI Bot Local Dev')"
echo "4. Paste the key above"
echo "5. Click 'Add SSH key'"
echo ""
echo "After adding the key, update your git remote:"
echo "git remote set-url origin git@github.com:TomerGutman1/ceci-bot-chain.git"
echo ""
echo "Then test with: ssh -T git@github.com"