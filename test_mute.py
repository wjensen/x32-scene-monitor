#!/usr/bin/env python3
"""
Test different OSC addresses for muting X32 channels
"""

import socket
import struct
import sys
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

def test_mute_addresses(ip_address="192.168.1.100", port=10023):
    """Test different OSC addresses for muting"""
    
    print(f"🔇 Testing different mute addresses on X32 at {ip_address}:{port}")
    print("=" * 60)
    
    # Different possible mute addresses
    mute_addresses = [
        "/ch/01/mix/on",           # Standard mute
        "/ch/01/mix/mute",         # Alternative mute
        "/ch/01/mix/01/on",        # Some consoles use this format
        "/ch/01/mix/01/mute",      # Alternative format
        "/ch/01/mix/01/on",        # Another variation
        "/ch/01/mix/01/mute",      # Another variation
        "/ch/01/mix/01/on",        # Another variation
        "/ch/01/mix/01/mute",      # Another variation
    ]
    
    for i, address in enumerate(mute_addresses, 1):
        print(f"{i}. Testing mute address: {address}")
        
        # Try to mute
        if send_osc_message(ip_address, port, address, False):
            print(f"   ✅ Sent mute command")
            time.sleep(1)
            
            # Try to unmute
            if send_osc_message(ip_address, port, address, True):
                print(f"   ✅ Sent unmute command")
            else:
                print(f"   ❌ Failed to send unmute command")
        else:
            print(f"   ❌ Failed to send mute command")
        
        time.sleep(1)
        print()
    
    print("🎯 Test completed! Check your X32 console for:")
    print("   - Channel 1 mute button toggling on/off")
    print("   - Any error messages on the X32 screen")

if __name__ == "__main__":
    ip_address = sys.argv[1] if len(sys.argv) > 1 else "192.168.1.100"
    test_mute_addresses(ip_address, 10023) 