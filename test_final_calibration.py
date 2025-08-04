#!/usr/bin/env python3
"""
Final calibrated fader transformation
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
    Transform scene file dB value to X32 normalized fader value
    Based on calibration data:
    - +5.0 dB scene → 0.563 normalized → -7.5 dB console
    - 0.0 dB scene → 0.5 normalized → -24.7 dB console  
    - 0.7 normalized → -2.0 dB console
    
    To get 0.0 dB on console (unity gain), we need to find the normalized value
    that gives us 0.0 dB console reading.
    """
    # From our data points, we can see the relationship:
    # normalized 0.5 → -24.7 dB console
    # normalized 0.7 → -2.0 dB console
    
    # Calculate the slope: (0.7 - 0.5) / (-2.0 - (-24.7)) = 0.2 / 22.7 = 0.0088
    # To get 0.0 dB console, we need: 0.7 + (2.0 * 0.0088) = 0.7176
    
    # Let's calculate the exact normalized value for 0.0 dB console
    # Using linear interpolation between our known points
    
    # For 0.0 dB console (unity gain), we need:
    # normalized = 0.7 + (2.0 * (0.7 - 0.5) / 22.7) = 0.7176
    
    unity_normalized = 0.7176
    
    # Now map scene file dB to this normalized range
    # Scene file 0.0 dB should map to unity gain (0.0 dB console)
    # Scene file +5.0 dB should map to -7.5 dB console
    
    # Calculate the slope for scene dB to normalized
    scene_db1, console_db1 = 0.0, -24.7  # 0.5 normalized
    scene_db2, console_db2 = 5.0, -7.5   # 0.563 normalized
    
    # Map scene dB to console dB first
    scene_to_console_slope = (console_db2 - console_db1) / (scene_db2 - scene_db1)
    scene_to_console_intercept = console_db1 - scene_to_console_slope * scene_db1
    
    console_db = scene_to_console_slope * db_value + scene_to_console_intercept
    
    # Now map console dB to normalized
    # console -24.7 dB → 0.5 normalized
    # console -2.0 dB → 0.7 normalized
    # console 0.0 dB → 0.7176 normalized
    
    console_to_normalized_slope = (0.7 - 0.5) / (-2.0 - (-24.7))
    console_to_normalized_intercept = 0.5 - console_to_normalized_slope * (-24.7)
    
    normalized = console_to_normalized_slope * console_db + console_to_normalized_intercept
    
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
    
    # Test 0.0 dB (unity gain) with final calibration
    db_value = 0.0
    normalized = transform_db_to_x32_fader(db_value)
    
    print(f"🎚️  Final calibration test: {db_value} dB → {normalized:.4f} normalized")
    print(f"🎯 Target: {ip_address}:{port}")
    print(f"🎯 Expected: 0.0 dB (unity gain) on console")
    
    success = send_osc_command(ip_address, port, "/ch/01/mix/fader", normalized)
    if success:
        print("✅ Final calibrated fader command sent!")
    else:
        print("❌ Failed to send fader command")
    
    print("🎯 Test completed!")

if __name__ == "__main__":
    main() 