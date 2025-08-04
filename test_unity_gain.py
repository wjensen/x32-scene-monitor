#!/usr/bin/env python3
"""
Test to find the normalized value that gives 0.0 dB (unity gain)
"""

import socket
import struct

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
        message = create_osc_message(address, value)
        sock.sendto(message, (ip_address, port))
        sock.close()
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    ip_address = "192.168.1.116"
    port = 10023
    
    # Based on our previous tests, let's try to find what gives us 0.0 dB
    # We know 0.563 gave us -7.5 dB, so let's try a higher value
    test_value = 0.7  # Try a higher normalized value
    
    print(f"🎚️  Testing normalized value: {test_value}")
    print(f"🎯 Target: {ip_address}:{port}")
    print(f"🎯 Goal: Find the value that gives us 0.0 dB (unity gain)")
    
    success = send_osc_command(ip_address, port, "/ch/01/mix/fader", test_value)
    if success:
        print("✅ Fader command sent!")
    else:
        print("❌ Failed to send fader command")
    
    print("🎯 Test completed!")

if __name__ == "__main__":
    main() 