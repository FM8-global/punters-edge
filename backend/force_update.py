#!/usr/bin/env python3
"""Force update predictions.html on PythonAnywhere"""
import subprocess
import os
import sys

repo_path = "/home/fm8/punter-edge"

try:
    # Change to repo directory
    os.chdir(repo_path)

    # Force fetch from remote
    print("Fetching from remote...")
    subprocess.run(["git", "fetch", "origin", "main"], check=True)

    # Force checkout the latest version
    print("Checking out latest from origin...")
    subprocess.run(["git", "checkout", "-f", "origin/main"], check=True)

    # Reset to ensure clean state
    print("Resetting to origin/main...")
    subprocess.run(["git", "reset", "--hard", "origin/main"], check=True)

    # Verify file exists
    pred_file = os.path.join(repo_path, "backend/static/predictions.html")
    if os.path.exists(pred_file):
        with open(pred_file, 'r') as f:
            content = f.read()
            if "fetch('/races'" in content:
                print("[SUCCESS] predictions.html has been updated with /races endpoint")
            else:
                print("[ERROR] predictions.html still has old /bets endpoint")
                sys.exit(1)
    else:
        print(f"[ERROR] File not found: {pred_file}")
        sys.exit(1)

    # Touch WSGI to reload
    print("Reloading WSGI...")
    wsgi_file = "/var/www/FM8Global_pythonanywhere_com_wsgi.py"
    os.utime(wsgi_file, None)

    print("[SUCCESS] Force update completed")

except Exception as e:
    print(f"[ERROR] {str(e)}")
    sys.exit(1)
