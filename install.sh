#!/bin/bash
# VIVID Agent Complete Setup — All Skills, All Repos, Full Tool Suite
# Based on Jakin's exact setup

set -e

VIVID_DIR="$HOME/vivid-agent"
WORKSPACE="$HOME/.openclaw/workspace"

echo ""
echo "========================================"
echo "   🦆 VIVID Agent — Complete Setup"
echo "========================================"
echo ""

# 1. Clone VIVID Agent
echo "📦 Step 1: Installing VIVID Agent..."
if [ ! -d "$VIVID_DIR/.git" ]; then
    git clone https://github.com/jjakinn/vivid-agent.git "$VIVID_DIR"
fi
cd "$VIVID_DIR"

# 2. Install Python deps
echo "📦 Step 2: Installing dependencies..."
python3 -m pip install -e . -q 2>/dev/null || python3 -m pip install requests -q

# 3. Clone all repos
echo "📦 Step 3: Cloning all repositories..."
python3 "$VIVID_DIR/vivid/repos.py" clone-all

# 4. Install all skills
echo "📦 Step 4: Installing skills..."
python3 "$VIVID_DIR/vivid/skills.py" install-all

# 5. Set up configs
echo "📦 Step 5: Configuring VIVID Agent..."
python3 "$VIVID_DIR/vivid/setup.py" init

echo ""
echo "========================================"
echo "   ✅ Setup Complete!"
echo "========================================"
echo ""
echo "Run: vivid chat"
echo "Or:  cd $VIVID_DIR && ./vivid.sh chat"
echo ""
