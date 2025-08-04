#!/usr/bin/env python3
"""
Direct fader test
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
        print(f"🌐 Target: {ip_address}:{port}")
        
        message = create_osc_message(address, value)
        print(f"📦 Message size: {len(message)} bytes")
        
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
    
    print("🎚️  Testing fader command directly...")
    print(f"🎯 Target: {ip_address}:{port}")
    print()
    
    # Test fader to 0dB
    success = send_osc_command(ip_address, port, "/ch/01/mix/fader", 0.0)
    if success:
        print("✅ Fader command sent!")
    else:
        print("❌ Failed to send fader command")
    
    print("⏳ Waiting 3 seconds...")
    time.sleep(3)
    
    # Test fader to -20dB
    success = send_osc_command(ip_address, port, "/ch/01/mix/fader", -20.0)
    if success:
        print("✅ Fader command sent!")
    else:
        print("❌ Failed to send fader command")
    
    print("🎯 Test completed!")

if __name__ == "__main__":
    main() 