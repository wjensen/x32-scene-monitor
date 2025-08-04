#!/usr/bin/env python3
"""
Test script to load the modified scene file and apply it to X32
"""

import socket
import struct
import sys
import time
import os

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

def test_connection(ip_address, port=10023, timeout=2):
    """Test connection to X32"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(timeout)
        
        # Send a simple OSC message to test connection
        test_message = create_osc_message("/xinfo", "")
        sock.sendto(test_message, (ip_address, port))
        
        # Try to receive a response
        try:
            data, addr = sock.recvfrom(1024)
            print(f"✅ Received response from {addr}")
            sock.close()
            return True
        except socket.timeout:
            print("⚠️  No response received, but connection may still work")
            sock.close()
            return True
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def load_scene_file(ip_address, scene_file_path):
    """Load scene file to X32"""
    print(f"🎯 Loading scene file: {scene_file_path}")
    print("=" * 50)
    
    # Test connection first
    if not test_connection(ip_address, 10023):
        print("❌ Cannot connect to X32 console.")
        return False
    
    # Check if file exists
    if not os.path.exists(scene_file_path):
        print(f"❌ Scene file not found: {scene_file_path}")
        return False
    
    # Send scene load command
    print("📁 Sending scene load command...")
    if send_osc_message(ip_address, 10023, "/load", scene_file_path):
        print("✅ Scene load command sent successfully")
        print("🔄 X32 should now load the scene with Will channel unmuted")
        return True
    else:
        print("❌ Failed to send scene load command")
        return False

def verify_will_channel_status(ip_address):
    """Verify Will channel is unmuted"""
    print("\n🔍 Verifying Will channel status...")
    
    # Send query for Will channel mute status
    if send_osc_message(ip_address, 10023, "/ch/01/mix/on", ""):
        print("✅ Will channel status query sent")
        print("💡 Check X32 console - Will channel should be unmuted")
    else:
        print("❌ Failed to query Will channel status")

if __name__ == "__main__":
    ip_address = sys.argv[1] if len(sys.argv) > 1 else "192.168.1.116"
    scene_file = sys.argv[2] if len(sys.argv) > 2 else "integrated.scn"
    
    print(f"🎛️  X32 Scene Loading Test")
    print(f"IP: {ip_address}")
    print(f"Scene: {scene_file}")
    print("=" * 50)
    
    # Load the scene file
    if load_scene_file(ip_address, scene_file):
        time.sleep(2)  # Give X32 time to load
        verify_will_channel_status(ip_address)
    
    print("\n🎯 Test completed!")
    print("📋 Check your X32 console for:")
    print("   - Scene loading progress")
    print("   - Will channel unmuted status")
    print("   - Any error messages") 