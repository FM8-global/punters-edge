#!/usr/bin/env python3
"""
PunterEdge Auto-Deployment Setup
Sets up GitHub Actions to auto-deploy to PythonAnywhere
"""

import subprocess
import sys
import os
import json
from pathlib import Path

def run_command(cmd, description):
    """Run a shell command and return output"""
    print(f"\n📋 {description}")
    print(f"   Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"   ❌ Error: {result.stderr}")
            return None
        print(f"   ✅ Success")
        return result.stdout.strip()
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return None

def main():
    print("=" * 60)
    print("PunterEdge GitHub Actions Auto-Deployment Setup")
    print("=" * 60)

    # Step 1: Generate SSH key on PythonAnywhere
    print("\n[STEP 1] Generate SSH key on PythonAnywhere")
    print("-" * 60)
    print("""
1. SSH into PythonAnywhere:
   ssh fm8global@ssh.pythonanywhere.com

2. Run these commands:
   ssh-keygen -t rsa -b 4096 -f ~/.ssh/github_actions -N ""
   cat ~/.ssh/github_actions

3. Copy the ENTIRE output (including BEGIN/END lines)
   """)

    ssh_key = input("Paste the private SSH key here:\n").strip()

    if not ssh_key.startswith("-----BEGIN"):
        print("❌ Invalid SSH key format")
        return False

    print("✅ SSH key received")

    # Step 2: Authorize key on PythonAnywhere
    print("\n[STEP 2] Authorize SSH key on PythonAnywhere")
    print("-" * 60)
    print("""
SSH back into PythonAnywhere and run:
   ssh-keygen -y -f ~/.ssh/github_actions >> ~/.ssh/authorized_keys

Once done, type 'done' here:""")

    auth_status = input().strip().lower()
    if auth_status != "done":
        print("⚠️  Skipping authorization verification")
    else:
        print("✅ SSH key authorized")

    # Step 3: Add secret to GitHub
    print("\n[STEP 3] Add SSH key to GitHub Secrets")
    print("-" * 60)
    print("""
1. Go to: https://github.com/FM8-global/punters-edge/settings/secrets/actions
2. Click "New repository secret"
3. Name: PYTHONANYWHERE_SSH_KEY
4. Value: [paste the SSH key you provided above]
5. Click "Add secret"

Once done, type 'done' here:""")

    github_status = input().strip().lower()
    if github_status != "done":
        print("⚠️  Skipping GitHub verification")
    else:
        print("✅ GitHub secret added")

    # Step 4: Test deployment
    print("\n[STEP 4] Test Auto-Deployment")
    print("-" * 60)
    print("""
To test the auto-deployment:
1. Make a small change to any file in the repo
2. Commit and push to main:
   git add .
   git commit -m "Test auto-deployment"
   git push origin main

3. Check GitHub Actions tab for deployment status:
   https://github.com/FM8-global/punters-edge/actions

The workflow should:
- Connect to PythonAnywhere
- Pull latest code
- Reload the app
- Complete in ~10 seconds
""")

    print("\n" + "=" * 60)
    print("✅ Setup Complete!")
    print("=" * 60)
    print("\nFrom now on, every push to main will auto-deploy!")
    print("\nNext steps:")
    print("1. Make sure all 3 steps above are completed")
    print("2. Test with a small commit")
    print("3. Check the GitHub Actions tab to verify deployment")

if __name__ == "__main__":
    main()
