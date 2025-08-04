#!/usr/bin/env python3
"""
Test calibrated fader transformation
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

def transform_db_to_x32_fader(db_value):
    """
    Transform dB value to X32 fader value based on calibration:
    +5.0 dB → 0.563 normalized → -7.5 dB on console
    0.0 dB → 0.5 normalized → -24.7 dB on console
    """
    # Based on the calibration data, it seems the X32 expects
    # a different range. Let me try a simple linear mapping:
    
    # Map scene file dB to console dB
    # +5.0 dB scene → -7.5 dB console
    # 0.0 dB scene → -24.7 dB console
    
    # Calculate the slope and intercept
    scene_db1, console_db1 = 5.0, -7.5
    scene_db2, console_db2 = 0.0, -24.7
    
    slope = (console_db2 - console_db1) / (scene_db2 - scene_db1)
    intercept = console_db1 - slope * scene_db1
    
    # Apply the transformation
    console_db = slope * db_value + intercept
    
    # Convert console dB to normalized (assuming -60 to +10 range)
    if console_db <= -60:
        return 0.0
    elif console_db >= 10:
        return 1.0
    else:
        # Convert dB to linear: 10^(dB/20)
        linear = 10 ** (console_db / 20.0)
        # Normalize to 0.0-1.0 range
        normalized = (linear - 0.001) / (3.16 - 0.001)
        return max(0.0, min(1.0, normalized))

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
    
    # Test 0.0 dB (unity gain) with calibrated transformation
    db_value = 0.0
    normalized = transform_db_to_x32_fader(db_value)
    
    print(f"🎚️  Testing calibrated fader: {db_value} dB → {normalized:.3f} normalized")
    print(f"🎯 Target: {ip_address}:{port}")
    
    success = send_osc_command(ip_address, port, "/ch/01/mix/fader", normalized)
    if success:
        print("✅ Calibrated fader command sent!")
    else:
        print("❌ Failed to send fader command")
    
    print("🎯 Test completed!")

if __name__ == "__main__":
    main() 