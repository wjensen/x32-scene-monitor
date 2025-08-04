#!/usr/bin/env python3
"""
Test script to trigger file change detection
"""

import time
import os

def test_file_change():
    """Make a small change to test file monitoring"""
    
    print("🧪 Testing file change detection...")
    
    # Read current file
    with open('integrated.scn', 'r') as f:
        content = f.read()
    
    # Make a small change - add a comment
    if '# Test change' not in content:
        # Add a comment at the top
        content = '# Test change - ' + time.strftime('%H:%M:%S') + '\n' + content
        print("📝 Adding test comment to file...")
    else:
        # Update the existing comment
        lines = content.split('\n')
        lines[0] = '# Test change - ' + time.strftime('%H:%M:%S')
        content = '\n'.join(lines)
        print("📝 Updating test comment in file...")
    
    # Write back to file
    with open('integrated.scn', 'w') as f:
        f.write(content)
    
    print("✅ File modified - X32 Scene Monitor should detect this change")
    print("📋 Check the app UI for change detection messages")

if __name__ == "__main__":
    test_file_change() 