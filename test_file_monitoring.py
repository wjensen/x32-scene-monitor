#!/usr/bin/env python3
"""
Test file monitoring directly
"""

import os
import time
import hashlib

def test_file_monitoring():
    """Test if file monitoring is working"""
    filepath = "integrated.scn"
    
    print("🧪 Testing file monitoring...")
    print(f"📁 File: {filepath}")
    
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return
    
    # Read current file
    with open(filepath, 'r') as f:
        content = f.read()
    
    print(f"📊 File size: {len(content)} bytes")
    
    # Calculate hash
    file_hash = hashlib.md5(content.encode()).hexdigest()
    print(f"🔢 File hash: {file_hash[:8]}...")
    
    # Check if file contains the expected content
    if "/ch/01/mix OFF" in content:
        print("✅ File contains: /ch/01/mix OFF (muted)")
    elif "/ch/01/mix ON" in content:
        print("✅ File contains: /ch/01/mix ON (unmuted)")
    else:
        print("❌ File doesn't contain expected mute status")
    
    # List all .scn files
    print("\n📂 All .scn files in directory:")
    for file in os.listdir('.'):
        if file.endswith('.scn'):
            print(f"   - {file}")
    
    # Check for temporary files
    print("\n🔍 Checking for temporary files:")
    for file in os.listdir('.'):
        if file.startswith('.') or '!' in file:
            print(f"   - {file} (temporary file)")

if __name__ == "__main__":
    test_file_monitoring() 