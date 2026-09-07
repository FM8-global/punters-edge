#!/usr/bin/env python3
"""
Reset admin password for PunterEdge on Render.
Usage: python reset_admin_password.py [new_password]
Default password: admin123
"""

import sys
import os
from auth import set_admin_password, ADMIN_EMAIL
from dotenv import load_dotenv

load_dotenv()

def main():
    password = sys.argv[1] if len(sys.argv) > 1 else "admin123"

    print(f"Resetting password for {ADMIN_EMAIL}...")

    if set_admin_password(password):
        print(f"✅ Password reset successfully!")
        print(f"   Email: {ADMIN_EMAIL}")
        print(f"   Password: {password}")
    else:
        print("❌ Failed to reset password")
        sys.exit(1)

if __name__ == "__main__":
    main()
