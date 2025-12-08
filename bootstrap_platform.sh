#!/usr/bin/env bash
set -e

# Make sure needed dirs exist (idempotent)
mkdir -p docs
mkdir -p infra/nginx
mkdir -p platform/plugins/didlab-gym/templates
mkdir -p platform/plugins/didlab-gym/static
mkdir -p platform/plugins/didlab-courses
mkdir -p platform/plugins/didlab-contests
mkdir -p platform/plugins/didlab-dashboard
mkdir -p challenges
mkdir -p tools
mkdir -p data
touch data/.gitkeep

# --------- .gitignore ---------
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.pyc

# Editors
.idea/
.vscode/

# OS junk
.DS_Store

# Docker data
data/
infra/db-data/
infra/ctfd-uploads/

# Node / front-end (if added later)
node_modules/

# Virtualenvs
venv/
.env
EOF

# --------- README.md ---------
cat > README.md << 'EOF'
# DIDLab CTF Platform

A long-term, course-integrated CTF and challenge platform for:

- Introduction to Cybersecurity
- Ethical Hacking & Penetration Testing
- Cryptographic Applications
- Open practice (Gym) and contests

## Quick start (Ubuntu 24.04, dev mode)

Prereqs (run as a user with sudo):

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin git
sudo usermod -aG docker "$USER"
# Log out and back in so docker group takes effect
