#!/usr/bin/env python3
"""
Script to parse scene file and apply changes to X32 console
"""

import socket
import struct
import sys
import time
import os
import re

def create_osc_message(address, *args):
    """Create OSC message"""
    message = address.encode('utf-8')
    message += b'\x00' * (4 - len(message) % 4)

    type_tags = ','
    for arg in args:
        if isinstance(arg, bool):
            type_tags += 'T' if arg else 'F'
        elif isinstance(arg, int):
            type_tags += 'i'
        elif isinstance(arg, float):
            type_tags += 'f'
        elif isinstance(arg, str):
            type_tags += 's'

    message += type_tags.encode('utf-8')
    message += b'\x00' * (4 - len(type_tags) % 4)

    for arg in args:
        if isinstance(arg, bool):
            pass
        elif isinstance(arg, int):
            message += struct.pack('>i', arg)
        elif isinstance(arg, float):
            message += struct.pack('>f', arg)
        elif isinstance(arg, str):
            message += arg.encode('utf-8')
            message += b'\x00' * (4 - len(arg.encode('utf-8')) % 4)

    return message

def send_osc_message(ip_address, port, address, *args):
    """Send OSC message to X32"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2)
        message = create_osc_message(address, *args)
        sock.sendto(message, (ip_address, port))
        sock.close()
        return True
    except Exception as e:
        print(f"Error sending OSC message: {e}")
        return False

def parse_scene_file(filepath):
    """Parse scene file and extract channel settings"""
    changes = []
    
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Parse channel mix settings
            if line.startswith('/ch/') and '/mix ' in line:
                # Format: /ch/01/mix OFF  +8.1 ON +24 OFF   -oo
                parts = line.split()
                if len(parts) >= 3:
                    channel = parts[0]  # /ch/01/mix
                    mute_status = parts[1]  # OFF/ON
                    fader_level = parts[2]  # +8.1
                    
                    # Convert to OSC commands
                    if channel.startswith('/ch/') and channel.endswith('/mix'):
                        channel_num = channel.split('/')[2]
                        
                        # Mute status
                        mute_address = f"/ch/{channel_num}/mix/on"
                        mute_value = mute_status == "ON"
                        changes.append(("MUTE", channel_num, mute_address, mute_value))
                        
                        # Fader level
                        try:
                            fader_value = float(fader_level)
                            fader_address = f"/ch/{channel_num}/mix/fader"
                            changes.append(("FADER", channel_num, fader_address, fader_value))
                        except ValueError:
                            pass  # Skip if fader level is not a number
        
        return changes
        
    except Exception as e:
        print(f"Error parsing scene file: {e}")
        return []

def apply_scene_changes(ip_address, scene_file_path):
    """Apply scene file changes to X32"""
    print(f"🎯 Applying scene changes from: {scene_file_path}")
    print("=" * 50)
    
    # Parse scene file
    changes = parse_scene_file(scene_file_path)
    
    if not changes:
        print("❌ No changes found in scene file")
        return False
    
    print(f"📋 Found {len(changes)} changes to apply")
    
    # Apply each change
    success_count = 0
    for action, channel, address, value in changes:
        print(f"🎛️  {action}: Channel {channel} | {address} = {value}")
        
        if send_osc_message(ip_address, 10023, address, value):
            print(f"✅ Success")
            success_count += 1
        else:
            print(f"❌ Failed")
        
        time.sleep(0.1)  # Small delay between commands
    
    print(f"\n🎯 Applied {success_count}/{len(changes)} changes successfully")
    return success_count > 0

if __name__ == "__main__":
    ip_address = sys.argv[1] if len(sys.argv) > 1 else "192.168.1.116"
    scene_file = sys.argv[2] if len(sys.argv) > 2 else "integrated.scn"
    
    print(f"🎛️  X32 Scene Change Application")
    print(f"IP: {ip_address}")
    print(f"Scene: {scene_file}")
    print("=" * 50)
    
    # Apply changes
    if apply_scene_changes(ip_address, scene_file):
        print("\n✅ Scene changes applied successfully!")
        print("📋 Check your X32 console for the changes")
    else:
        print("\n❌ Failed to apply scene changes") 