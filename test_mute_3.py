#!/usr/bin/env python3
"""
Test the specific mute command that worked
"""

import socket
import struct
import time

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

def send_osc_command(ip_address, port, address, value):
    """Send OSC command to X32"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        print(f"🎛️  Sending: {address} = {value}")
        
        message = create_osc_message(address, value)
        sock.sendto(message, (ip_address, port))
        sock.close()
        
        print(f"✅ Command sent successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    ip_address = "192.168.1.116"
    port = 10023
    
    print("🧪 Testing the mute command that worked...")
    print(f"🎯 Target: {ip_address}:{port}")
    print()
    
    # Test the specific command that worked
    print("🔧 Testing: /ch/01/mix/on = 0 (MUTE)")
    success = send_osc_command(ip_address, port, "/ch/01/mix/on", 0)
    if success:
        print("✅ MUTE command sent")
    print("⏳ Waiting 3 seconds...")
    time.sleep(3)
    
    print("🔧 Testing: /ch/01/mix/on = 1 (UNMUTE)")
    success = send_osc_command(ip_address, port, "/ch/01/mix/on", 1)
    if success:
        print("✅ UNMUTE command sent")
    print("⏳ Waiting 3 seconds...")
    time.sleep(3)
    
    print("🎯 Test completed!")
    print("💡 Did you see the Will channel mute and unmute?")

if __name__ == "__main__":
    main() 