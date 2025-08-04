#!/usr/bin/env python3
"""
Simple script to unmute Will channel
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

if __name__ == "__main__":
    ip_address = "192.168.1.116"
    port = 10023
    
    print(f"🎛️  Unmuting Will channel on X32 at {ip_address}:{port}")
    print("=" * 50)
    
    # Send unmute command for Will channel (Channel 1)
    if send_osc_message(ip_address, port, "/ch/01/mix/on", True):
        print("✅ Successfully sent unmute command for Will channel")
        print("🎵 Will channel should now be audible in the mains")
    else:
        print("❌ Failed to send unmute command") 