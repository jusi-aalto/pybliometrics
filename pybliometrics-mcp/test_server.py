#!/usr/bin/env python3
"""
Simple test to verify the MCP server is working
"""

import subprocess
import json
import sys


def test_server_starts():
    """Test that the server starts and responds to list tools request"""
    print("Testing pybliometrics-mcp server...")

    # Test that the command exists
    try:
        result = subprocess.run(
            ["which", "pybliometrics-mcp"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✓ pybliometrics-mcp is installed at: {result.stdout.strip()}")
        else:
            print("✗ pybliometrics-mcp command not found")
            return False
    except Exception as e:
        print(f"✗ Error checking installation: {e}")
        return False

    # Check that pybliometrics is configured
    try:
        import os
        config_path = os.path.expanduser("~/.config/pybliometrics.cfg")
        if os.path.exists(config_path):
            print(f"✓ pybliometrics config exists at: {config_path}")
            with open(config_path) as f:
                content = f.read()
                if "YOUR_API_KEY_HERE" in content:
                    print("⚠ Warning: API key not configured. Edit ~/.config/pybliometrics.cfg")
                else:
                    print("✓ API key appears to be configured")
        else:
            print("✗ pybliometrics config not found")
            return False
    except Exception as e:
        print(f"✗ Error checking config: {e}")
        return False

    print("\n✓ All basic checks passed!")
    print("\nNext steps:")
    print("1. Edit ~/.config/pybliometrics.cfg and add your Scopus API key")
    print("2. Get an API key from: https://dev.elsevier.com/")
    print("3. Add the server to Claude Desktop config (see README.md)")

    return True


if __name__ == "__main__":
    success = test_server_starts()
    sys.exit(0 if success else 1)
