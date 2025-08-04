#!/usr/bin/env python3
"""
Move Will channel fader
"""

import socket
import struct
import time
import sys

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

def move_will_fader(ip_address="192.168.1.116", fader_level=0.0):
    """Move Will channel fader to specified level"""
    
    print(f"🎛️  Moving Will channel fader to {fader_level}dB")
    print(f"IP: {ip_address}")
    print("=" * 40)
    
    # Send fader command
    if send_osc_message(ip_address, 10023, "/ch/01/mix/fader", fader_level):
        print(f"✅ Fader moved to {fader_level}dB")
        print("🎵 Check your X32 console - fader should have moved!")
        return True
    else:
        print(f"❌ Failed to move fader")
        return False

if __name__ == "__main__":
    # Get fader level from command line or use default
    fader_level = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
    ip_address = sys.argv[2] if len(sys.argv) > 2 else "192.168.1.116"
    
    move_will_fader(ip_address, fader_level) 