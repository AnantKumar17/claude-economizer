#!/usr/bin/env python3
"""
Prompt Economizer Installer
Run: python3 scripts/install.py
"""

import sys
import json
import os
import subprocess
import shutil
from pathlib import Path

REPO_DIR = Path(__file__).parent.parent.resolve()
CLAUDE_DIR = Path.home() / ".claude"
SKILLS_DIR = CLAUDE_DIR / "skills"
COMMANDS_DIR = CLAUDE_DIR / "commands"
SETTINGS_FILE = CLAUDE_DIR / "settings.json"
USER_DATA_DIR = CLAUDE_DIR / "prompt-economizer"

def step(msg: str):
    print(f"  [OK] {msg}")

def fail(msg: str):
    print(f"  [ERROR] {msg}")
    sys.exit(1)

def main():
    print("\n╔══════════════════════════════════╗")
    print("║   Prompt Economizer Installer    ║")
    print("╚══════════════════════════════════╝\n")

    # 1. Python version check
    if sys.version_info < (3, 8):
        fail(f"Python 3.8+ required. Found: {sys.version}")
    step(f"Python {sys.version.split()[0]} OK")

    # 2. Install dependencies
    print("\n[1/6] Installing dependencies...")
    # Try normal pip install first
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "anthropic>=0.40.0", "--quiet"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        # If externally-managed environment, try with --user flag
        print("  → Retrying with --user flag...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "anthropic>=0.40.0", "--user", "--quiet"],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            # On macOS/some Linux systems, try --break-system-packages as last resort
            if "externally-managed-environment" in result.stderr:
                print("  → Retrying with --break-system-packages flag (macOS detected)...")
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "anthropic>=0.40.0", "--user", "--break-system-packages", "--quiet"],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    step("anthropic package installed (--user --break-system-packages)")
                else:
                    print(f"  [WARN] Warning: Could not install anthropic package")
                    print(f"  Please install manually:")
                    print(f"    pip3 install anthropic --user --break-system-packages")
            else:
                print(f"  [WARN] Warning: Could not install anthropic package")
                print(f"  Please install manually: pip3 install anthropic --user")
        else:
            step("anthropic package installed (--user)")
    else:
        step("anthropic package installed")

    # 3. Make hook executable
    print("\n[2/6] Setting permissions...")
    hook_sh = REPO_DIR / "hooks" / "economizer.sh"
    hook_sh.chmod(0o755)
    step(f"chmod +x {hook_sh}")

    # 4. Create user data directory
    print("\n[3/6] Creating user data directory...")
    USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
    step(f"Created {USER_DATA_DIR}")

    # 5. Register hook in settings.json
    print("\n[4/6] Registering hook in ~/.claude/settings.json...")
    CLAUDE_DIR.mkdir(parents=True, exist_ok=True)

    settings = {}
    if SETTINGS_FILE.exists():
        with open(SETTINGS_FILE) as f:
            try:
                settings = json.load(f)
            except json.JSONDecodeError:
                settings = {}

    hook_entry = {
        "hooks": [{
            "type": "command",
            "command": str(REPO_DIR / "hooks" / "economizer.sh")
        }]
    }

    if "hooks" not in settings:
        settings["hooks"] = {}
    if "UserPromptSubmit" not in settings["hooks"]:
        settings["hooks"]["UserPromptSubmit"] = []

    # Check if already registered
    already_registered = any(
        str(REPO_DIR) in json.dumps(entry)
        for entry in settings["hooks"]["UserPromptSubmit"]
    )

    if not already_registered:
        settings["hooks"]["UserPromptSubmit"].append(hook_entry)

    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)
    step("Hook registered in settings.json")

    # 6. Install skill and commands
    print("\n[5/6] Installing skills and commands...")
    SKILLS_DIR.mkdir(parents=True, exist_ok=True)
    COMMANDS_DIR.mkdir(parents=True, exist_ok=True)

    shutil.copy(REPO_DIR / "skills" / "prompt-economizer.md",
                SKILLS_DIR / "prompt-economizer.md")
    step("Skill installed")

    for cmd_file in (REPO_DIR / "commands").glob("*.md"):
        shutil.copy(cmd_file, COMMANDS_DIR / cmd_file.name)
        step(f"Command installed: /{cmd_file.stem}")

    # 7. Write default user config (only if not exists)
    print("\n[6/6] Writing user config...")
    user_config_path = USER_DATA_DIR / "config.json"
    if not user_config_path.exists():
        with open(REPO_DIR / "config" / "default-config.json") as f:
            default = json.load(f)
        with open(user_config_path, "w") as f:
            json.dump(default, f, indent=2)
        step(f"Config written to {user_config_path}")
    else:
        step("Existing config preserved")

    print("\n╔══════════════════════════════════╗")
    print("║   Installation Complete!         ║")
    print("╚══════════════════════════════════╝\n")
    print("Next steps:")
    print(f"  1. Set your API key:")
    print(f"     export ANTHROPIC_API_KEY=\"your-key-here\"")
    print(f"")
    print(f"     SAP employees: See docs/SAP_SETUP.md for proxy setup")
    print(f"")
    print(f"  2. Restart Claude Code (or open a new session)")
    print(f"  3. Type any prompt — it will be automatically optimized")
    print(f"  4. Use /economizer-stats to see token savings")
    print(f"  5. Use /economizer-toggle to enable/disable")
    print(f"\nConfig: {user_config_path}")
    print(f"Logs:   {USER_DATA_DIR / 'economizer.log'}")
    print(f"Docs:   {REPO_DIR / 'docs' / 'SAP_SETUP.md'} (for proxy users)\n")

if __name__ == "__main__":
    main()
