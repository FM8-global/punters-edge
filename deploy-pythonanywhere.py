#!/usr/bin/env python3
"""
Automated PythonAnywhere Deployment Script for PunterEdge
Deploys the full app with authentication in one command
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path

# Colors for output
GREEN = '\033[92m'
BLUE = '\033[94m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def print_header(msg):
    print(f"\n{BLUE}{'='*60}")
    print(f"{msg}")
    print(f"{'='*60}{RESET}\n")

def print_success(msg):
    print(f"{GREEN}[OK] {msg}{RESET}")

def print_error(msg):
    print(f"{RED}[ERROR] {msg}{RESET}")

def print_info(msg):
    print(f"{YELLOW}[>] {msg}{RESET}")

def check_dependencies():
    """Check if required tools are installed"""
    print_header("Checking Dependencies")

    required = {
        'git': 'Git',
        'python': 'Python 3',
    }

    for cmd, name in required.items():
        try:
            subprocess.run([cmd, '--version'], capture_output=True, check=True)
            print_success(f"{name} installed")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print_error(f"{name} not found. Please install it first.")
            return False

    return True

def get_credentials():
    """Get PythonAnywhere credentials from user"""
    print_header("PythonAnywhere Login")
    print_info("Go to https://www.pythonanywhere.com and sign up first if you haven't")
    print()

    username = input(f"{YELLOW}Username (e.g., fm8): {RESET}").strip()

    # Check if user has API token instead
    use_token = input(f"{YELLOW}Do you have an API token? (y/n) [n]: {RESET}").strip().lower()

    if use_token == 'y':
        api_token = input(f"{YELLOW}PythonAnywhere API Token: {RESET}").strip()
        return username, api_token, True
    else:
        print_info("We'll use GitHub to deploy instead (simpler, no password needed)")
        return username, None, False

def setup_git_repo():
    """Prepare git repository for deployment"""
    print_header("Preparing Git Repository")

    repo_dir = Path(__file__).parent

    # Check if it's a git repo
    if not (repo_dir / '.git').exists():
        print_info("Initializing git repository...")
        subprocess.run(['git', 'init'], cwd=repo_dir, check=True)
        subprocess.run(['git', 'add', '.'], cwd=repo_dir, check=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=repo_dir, check=True)
        print_success("Git repository initialized")
    else:
        print_success("Git repository exists")

    return repo_dir

def create_pythonanywhere_config(username):
    """Create configuration file for PythonAnywhere setup"""
    print_header("Creating Configuration")

    config = {
        "username": username,
        "domain": f"{username.lower()}.pythonanywhere.com",
        "app_path": f"/home/{username}/punter-edge",
        "working_dir": f"/home/{username}/punter-edge/backend",
        "venv_name": "punter-edge",
        "python_version": "3.10",
        "api_key": "c9edb4f8-4c7f-4a20-b0a5-edbac822e0ec"
    }

    config_file = Path(__file__).parent / '.pythonanywhere-config.json'
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)

    print_success(f"Configuration saved")
    return config

def create_wsgi_file(username):
    """Create WSGI configuration file"""
    print_header("Creating WSGI Configuration")

    wsgi_content = f"""
import sys
import os

# Add your project directory to the sys.path
path = '/home/{username}/punter-edge/backend'
if path not in sys.path:
    sys.path.append(path)

# Set environment variable for API key
os.environ['API_KEY'] = 'c9edb4f8-4c7f-4a20-b0a5-edbac822e0ec'

# Import the FastAPI app
from main import app as application
"""

    wsgi_file = Path(__file__).parent / 'backend' / 'pythonanywhere_wsgi.py'
    with open(wsgi_file, 'w') as f:
        f.write(wsgi_content.strip())

    print_success(f"WSGI file created: {wsgi_file}")
    return wsgi_file

def create_setup_script(username):
    """Create bash script for PythonAnywhere setup"""
    print_header("Creating Setup Script")

    setup_script = f"""#!/bin/bash
set -e

echo "Setting up PunterEdge on PythonAnywhere..."

# Navigate to app directory
cd /home/{username}/punter-edge/backend

# Create virtual environment
python3.10 -m venv {username}_venv
source {username}_venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

echo "Setup complete!"
echo "Next steps:"
echo "1. Log in to pythonanywhere.com"
echo "2. Go to Web tab"
echo "3. Add new web app -> Python 3.10"
echo "4. Set source code to: /home/{username}/punter-edge"
echo "5. Set working directory to: /home/{username}/punter-edge/backend"
echo "6. Configure WSGI file: /home/{username}/punter-edge/backend/pythonanywhere_wsgi.py"
echo "7. Select virtualenv: {username}_venv"
echo "8. Add environment variable: API_KEY = c9edb4f8-4c7f-4a20-b0a5-edbac822e0ec"
echo "9. Reload web app"
echo "10. Visit: https://{username}.pythonanywhere.com/"
"""

    script_file = Path(__file__).parent / 'pythonanywhere-setup.sh'
    with open(script_file, 'w') as f:
        f.write(setup_script.strip())

    os.chmod(script_file, 0o755)
    print_success(f"Setup script created: {script_file}")
    return script_file

def create_deployment_guide(username):
    """Create step-by-step deployment guide"""
    print_header("Creating Deployment Guide")

    guide = f"""
# PythonAnywhere Deployment Guide for PunterEdge

## Quick Setup (Manual Steps Required)

Your username: **{username}**
Your domain: **https://{username}.pythonanywhere.com/**

### Step 1: Sign Up on PythonAnywhere
1. Go to https://www.pythonanywhere.com
2. Sign up with username: {username}
3. Verify email

### Step 2: Upload Your Code
In PythonAnywhere Bash console:

```bash
cd ~
git clone https://github.com/YOUR_USERNAME/punter-edge.git
cd punter-edge/backend
```

Or manually upload the `punter-edge` folder as ZIP.

### Step 3: Create Virtual Environment
In Bash console:

```bash
python3.10 -m venv punter-edge_venv
source punter-edge_venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Create Web App
1. Click "Web" tab
2. Click "Add a new web app"
3. Select "Python 3.10"
4. Keep defaults

### Step 5: Configure Web App
1. Click your app name under "Web"
2. Under "Code" section:
   - Source code: `/home/{username}/punter-edge`
   - Working directory: `/home/{username}/punter-edge/backend`

3. Under "WSGI configuration file":
   - Edit the file
   - Replace with content from: `pythonanywhere_wsgi.py`
   - Save

4. Under "Virtualenv":
   - Click "Enter path to a virtualenv"
   - Enter: `/home/{username}/punter-edge/backend/punter-edge_venv`

5. Scroll down, click "Environment variables"
   - Add: API_KEY = c9edb4f8-4c7f-4a20-b0a5-edbac822e0ec

### Step 6: Reload App
- Click green "Reload" button
- Wait for "Reloaded at..." message

### Step 7: Test
Visit: https://{username}.pythonanywhere.com/
- Should see login page
- Login as: info@fm8.global
- Should get token

## Your Live URLs

| URL | Purpose |
|-----|---------|
| https://{username}.pythonanywhere.com/ | Login page |
| https://{username}.pythonanywhere.com/docs | API docs |
| https://{username}.pythonanywhere.com/bets | Get predictions |

## Squarespace Card

Add this to your fm8-apps page:

```html
<div style="border: 2px solid #667eea; border-radius: 12px; padding: 24px; background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); margin: 20px 0;">
  <h3 style="color: #667eea; margin: 0 0 12px 0; font-size: 22px;">🏇 PunterEdge</h3>
  <p style="color: #555; font-size: 16px; margin: 0 0 16px 0;">AI Horse Racing Betting - Live odds analysis with AI predictions</p>

  <a href="https://{username}.pythonanywhere.com/"
     style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 14px 32px; border-radius: 8px; text-decoration: none; font-weight: 600;">
    Launch PunterEdge →
  </a>

  <p style="color: #999; font-size: 13px; margin-top: 12px;">Approved users only. Contact info@fm8.global</p>
</div>
```

## Troubleshooting

### "Module not found" error
- Make sure virtualenv is set correctly
- Run pip install again in bash console

### "No module named 'main'"
- Check working directory is set to backend folder
- Check source code path is correct

### "ConnectionError"
- Make sure API_KEY environment variable is set
- Check PuntersEdge API key is valid

## Support
- PythonAnywhere: help.pythonanywhere.com
- PuntersEdge API: puntersedge.online/developers
"""

    guide_file = Path(__file__).parent / 'PYTHONANYWHERE_GUIDE.md'
    with open(guide_file, 'w') as f:
        f.write(guide.strip())

    print_success(f"Deployment guide created: {guide_file}")
    return guide_file

def create_checklist(username):
    """Create deployment checklist"""
    checklist = f"""
# PythonAnywhere Deployment Checklist

Your username: **{username}**

## Pre-Deployment
- [ ] Signed up at pythonanywhere.com
- [ ] Verified email
- [ ] Have your password ready

## Deployment Steps
- [ ] Uploaded punter-edge code to PythonAnywhere
- [ ] Created virtual environment
- [ ] Installed Python dependencies
- [ ] Created web app (Python 3.10)
- [ ] Configured WSGI file
- [ ] Set source code path
- [ ] Set working directory
- [ ] Set virtualenv path
- [ ] Added API_KEY environment variable (c9edb4f8-4c7f-4a20-b0a5-edbac822e0ec)

## Testing
- [ ] Clicked Reload button
- [ ] Visited https://{username}.pythonanywhere.com/
- [ ] Saw login page
- [ ] Logged in with info@fm8.global
- [ ] Got auth token
- [ ] Tested /bets API endpoint

## Squarespace Integration
- [ ] Added PunterEdge card to fm8-apps page
- [ ] Updated domain URL in card
- [ ] Tested card link works

## Go Live
- [ ] Shared app link: https://{username}.pythonanywhere.com/
- [ ] Added approved users via admin panel
- [ ] Updated Squarespace page
"""

    checklist_file = Path(__file__).parent / 'DEPLOYMENT_CHECKLIST.md'
    with open(checklist_file, 'w') as f:
        f.write(checklist.strip())

    print_success(f"Checklist created: {checklist_file}")
    return checklist_file

def main():
    """Main deployment script"""
    print(f"\n{BLUE}============================================================")
    print(f"   PunterEdge -> PythonAnywhere Deployment Script")
    print(f"              Automated Setup")
    print(f"============================================================{RESET}\n")

    # Step 1: Check dependencies
    if not check_dependencies():
        print_error("Please install missing dependencies and try again.")
        sys.exit(1)

    # Step 2: Get credentials
    username, api_token, use_api = get_credentials()

    if not username:
        print_error("Username is required.")
        sys.exit(1)

    # Step 3: Prepare git repo
    repo_dir = setup_git_repo()

    # Step 4: Create configuration
    config = create_pythonanywhere_config(username)

    # Step 5: Create WSGI file
    wsgi_file = create_wsgi_file(username)

    # Step 6: Create setup script
    setup_script = create_setup_script(username)

    # Step 7: Create deployment guide
    guide_file = create_deployment_guide(username)

    # Step 8: Create checklist
    checklist_file = create_checklist(username)

    # Final summary
    print_header("Deployment Package Ready!")

    print(f"""
{GREEN}✓ All deployment files created!{RESET}

Your PythonAnywhere username: {YELLOW}{username}{RESET}
Your live domain: {YELLOW}https://{username}.pythonanywhere.com/{RESET}

{BLUE}Next Steps:{RESET}
1. Sign up at https://www.pythonanywhere.com (if you haven't already)
2. Follow the manual steps in: {YELLOW}PYTHONANYWHERE_GUIDE.md{RESET}
3. Use checklist to track progress: {YELLOW}DEPLOYMENT_CHECKLIST.md{RESET}

{BLUE}Key Files:{RESET}
- {YELLOW}pythonanywhere_wsgi.py{RESET} - WSGI configuration
- {YELLOW}pythonanywhere-setup.sh{RESET} - Bash setup script
- {YELLOW}PYTHONANYWHERE_GUIDE.md{RESET} - Step-by-step guide
- {YELLOW}DEPLOYMENT_CHECKLIST.md{RESET} - Progress tracker
- {YELLOW}.pythonanywhere-config.json{RESET} - Configuration

{BLUE}After Deployment:{RESET}
Your app will be live at:
→ {YELLOW}https://{username}.pythonanywhere.com/{RESET}

Add to Squarespace fm8-apps page:
→ Copy the Squarespace card code from PYTHONANYWHERE_GUIDE.md

{YELLOW}Questions?{RESET}
- PythonAnywhere: help.pythonanywhere.com
- PuntersEdge API: puntersedge.online/developers
- FM8: info@fm8.global

{GREEN}Ready to deploy!{RESET}
""")

if __name__ == "__main__":
    main()
