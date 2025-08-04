#!/usr/bin/env python3
"""
Fader movement demonstration - like the original test
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

def fader_demo():
    """Demonstrate fader movement"""
    
    ip_address = "192.168.1.116"
    port = 10023
    
    print("🎛️  Fader Movement Demonstration")
    print(f"Target: X32 at {ip_address}:{port}")
    print("=" * 50)
    
    # Step 1: Move fader down to -20dB
    print("1. Moving Will fader to -20dB...")
    if send_osc_message(ip_address, port, "/ch/01/mix/fader", -20.0):
        print("   ✅ Fader moved down to -20dB")
    else:
        print("   ❌ Failed to move fader")
    
    time.sleep(1)
    
    # Step 2: Move fader back to 0dB
    print("2. Moving Will fader back to 0dB...")
    if send_osc_message(ip_address, port, "/ch/01/mix/fader", 0.0):
        print("   ✅ Fader moved back to 0dB")
    else:
        print("   ❌ Failed to move fader")
    
    time.sleep(0.5)
    
    # Step 3: Mute the channel
    print("3. Muting Will channel...")
    if send_osc_message(ip_address, port, "/ch/01/mix/on", False):
        print("   ✅ Channel muted")
    else:
        print("   ❌ Failed to mute")
    
    time.sleep(1)
    
    # Step 4: Unmute the channel
    print("4. Unmuting Will channel...")
    if send_osc_message(ip_address, port, "/ch/01/mix/on", True):
        print("   ✅ Channel unmuted")
    else:
        print("   ❌ Failed to unmute")
    
    print("\n🎯 Demo completed!")
    print("📋 You should have seen:")
    print("   - Will fader move down to -20dB")
    print("   - Will fader move back up to 0dB")
    print("   - Mute button turn on/off")

if __name__ == "__main__":
    fader_demo() 