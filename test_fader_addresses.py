#!/usr/bin/env python3
"""
Test different fader address variations for X32
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
    
    print("🧪 Testing different fader address variations...")
    print(f"🎯 Target: {ip_address}:{port}")
    print("💡 Watch your X32 console - the fader should move!")
    print()
    
    # Test different fader address variations
    fader_addresses = [
        ("Standard fader", "/ch/01/mix/fader", 0.0),
        ("Alternative fader 1", "/ch/01/mix/fader", 0),
        ("Alternative fader 2", "/ch/01/mix/fader", -20.0),
        ("Alternative fader 3", "/ch/01/mix/fader", 10.0),
        ("Alternative address 1", "/ch/01/fader", 0.0),
        ("Alternative address 2", "/ch/01/fader", -20.0),
        ("Alternative address 3", "/ch/01/fader", 10.0),
        ("Alternative address 4", "/ch/01/mix/level", 0.0),
        ("Alternative address 5", "/ch/01/mix/level", -20.0),
        ("Alternative address 6", "/ch/01/mix/level", 10.0),
        ("Alternative address 7", "/ch/01/level", 0.0),
        ("Alternative address 8", "/ch/01/level", -20.0),
        ("Alternative address 9", "/ch/01/level", 10.0),
    ]
    
    for name, address, value in fader_addresses:
        print(f"🔧 {name}...")
        success = send_osc_command(ip_address, port, address, value)
        if success:
            print(f"✅ {name} command sent")
        else:
            print(f"❌ {name} command failed")
        print()
        time.sleep(3)  # 3 second delay to see effects
    
    print("🎯 All fader address tests completed!")
    print("💡 Check your X32 console - one of these should have moved the fader!")

if __name__ == "__main__":
    main() 