import os
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional

REPOS = {
    # Core Infrastructure
    "gitnexus": "https://github.com/abhigyanpatwari/GitNexus.git",
    "godot-mcp": "https://github.com/Coding-Solo/godot-mcp.git",
    
    # AI / ML
    "ComfyUI": "https://github.com/comfyanonymous/ComfyUI.git",
    "ai4animationpy": "https://github.com/facebookresearch/ai4animationpy.git",
    "lyra": "https://github.com/nv-tlabs/lyra.git",
    "the_well": "https://github.com/PolymathicAI/the_well.git",
    
    # Club Penguin / Game
    "ClubPenguin": "https://github.com/project-flipper/ClubPenguin.git",
    "cpadvanced-client": "https://github.com/clubpenguinadvanced/cpadvanced-client.git",
    "cpps-houdini": "https://github.com/solero/houdini.git",
    "cpps-mammoth": "https://github.com/wizguin/mammoth.git",
    "yukon-client": "https://github.com/wizguin/yukon.git",
    "yukon-server": "https://github.com/wizguin/yukon-server.git",
    "waddle-forever": "https://github.com/nhaar/Waddle-Forever.git",
    "cp-minigames": "https://github.com/Ep8Script/Club_Penguin_Minigames.git",
    "cp-swf": "https://github.com/abarichello/cp-swf.git",
    
    # API Projects
    "ssl-analyzer-api": "https://github.com/Glztch/ssl-analyzer-api.git",
    "leadvault-automation": "https://github.com/jjakinn/leadvault-automation.git",
    "leadvault-site": "https://github.com/jjakinn/leadvault-site.git",
    "rize-clone": "https://github.com/jjakinn/rize-clone.git",
    
    # Other
    "terminalphone": "https://github.com/dunamismax/terminalphone.git",
    "TitanEngine": "https://github.com/uberchel/TitanEngine.git",
    "carbonyl": "https://github.com/fathyb/carbonyl.git",
    "openscreen": "https://github.com/siddharthvaddem/openscreen.git",
    "claw-code": "https://github.com/ultraworkers/claw-code.git",
    "editor": "https://github.com/pascalorg/editor.git",
    "stenoai": "https://github.com/ruzin/stenoai.git",
    "RuView": "https://github.com/ruvnet/RuView.git",
    "tuitter": "https://github.com/bddicken/tuitter.git",
    "dimos": "https://github.com/dimensionalOS/dimos.git",
    "asimov-v0": "https://github.com/asimovinc/asimov-v0.git",
    "modly": "https://github.com/lightningpixel/modly.git",
    "OBLITERATUS": "https://github.com/elder-plinius/OBLITERATUS.git",
    "Claw3D": "https://github.com/iamlukethedev/Claw3D.git",
    "fff.nvim": "https://github.com/dmtrKovalenko/fff.nvim.git",
    "try-html-in-canvas": "https://github.com/tomasferrerasdev/try-html-in-canvas.git",
    "CL1_LLM_Encoder": "https://github.com/4R7I5T/CL1_LLM_Encoder.git",
    "CADAM": "https://github.com/Adam-CAD/CADAM.git",
    "PLFM_RADAR": "https://github.com/NawfalMotii79/PLFM_RADAR.git",
    "fly-brain": "https://github.com/eonsystemspbc/fly-brain.git",
    "Polymarketbot": "https://github.com/advaricorp/Polymarketbot.git",
}

def clone_all():
    """Clone all repositories"""
    home = Path.home()
    total = len(REPOS)
    cloned = 0
    skipped = 0
    failed = 0
    
    print(f"📦 Cloning {total} repositories...")
    
    for name, url in REPOS.items():
        dest = home / name
        if (dest / ".git").exists():
            print(f"  ⏭️  {name} (already exists)")
            skipped += 1
            continue
        
        print(f"  📥 {name}...", end=" ")
        try:
            result = subprocess.run(
                ["git", "clone", "--depth", "1", url, str(dest)],
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.returncode == 0:
                print("✅")
                cloned += 1
            else:
                print(f"❌ ({result.stderr[:100]})")
                failed += 1
        except Exception as e:
            print(f"❌ ({str(e)[:100]})")
            failed += 1
    
    print(f"\n✅ Done: {cloned} cloned, {skipped} skipped, {failed} failed")

def list_repos():
    """List all repositories and their status"""
    home = Path.home()
    print("📁 Repository Status:")
    for name, url in REPOS.items():
        dest = home / name
        if (dest / ".git").exists():
            print(f"  ✅ {name} ({dest})")
        else:
            print(f"  ❌ {name} (not cloned)")

def update_all():
    """Pull latest for all cloned repos"""
    home = Path.home()
    print("🔄 Updating all repositories...")
    for name in REPOS:
        dest = home / name
        if (dest / ".git").exists():
            print(f"  📥 {name}...", end=" ")
            try:
                result = subprocess.run(
                    ["git", "-C", str(dest), "pull", "--ff-only"],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                print("✅" if result.returncode == 0 else "⚠️")
            except Exception as e:
                print(f"❌ {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "clone-all":
            clone_all()
        elif sys.argv[1] == "list":
            list_repos()
        elif sys.argv[1] == "update-all":
            update_all()
        else:
            print(f"Unknown command: {sys.argv[1]}")
            print("Usage: python repos.py [clone-all|list|update-all]")
    else:
        clone_all()
