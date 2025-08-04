#!/usr/bin/env python3
"""
Test single fader value directly
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

def transform_db_to_normalized(db_value):
    """Transform dB value to normalized 0.0-1.0 range for X32"""
    try:
        if db_value <= -60:
            return 0.0
        elif db_value >= 10:
            return 1.0
        else:
            linear = 10 ** (db_value / 20.0)
            normalized = (linear - 0.001) / (3.16 - 0.001)
            return max(0.0, min(1.0, normalized))
    except:
        if db_value <= -60:
            return 0.0
        elif db_value >= 10:
            return 1.0
        else:
            return (db_value + 60) / 70.0

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
    
    # Test 0.0 dB (unity gain)
    db_value = 0.0
    normalized = transform_db_to_normalized(db_value)
    
    print(f"🎚️  Testing fader: {db_value} dB → {normalized:.3f} normalized")
    print(f"🎯 Target: {ip_address}:{port}")
    
    success = send_osc_command(ip_address, port, "/ch/01/mix/fader", normalized)
    if success:
        print("✅ Fader command sent!")
    else:
        print("❌ Failed to send fader command")
    
    print("🎯 Test completed!")

if __name__ == "__main__":
    main() 