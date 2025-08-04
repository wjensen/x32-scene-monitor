#!/usr/bin/env python3
"""
Refined calibrated fader transformation
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
    - 0.5 normalized → -24.7 dB console
    - 0.7 normalized → -2.0 dB console  
    - 0.7176 normalized → -10.0 dB console
    
    To get 0.0 dB console, we need to go higher than 0.7176
    """
    # From our latest data points:
    # 0.7 → -2.0 dB console
    # 0.7176 → -10.0 dB console (this seems wrong, let me recalculate)
    
    # Let me use the more reliable data points:
    # 0.5 → -24.7 dB console
    # 0.7 → -2.0 dB console
    
    # To get 0.0 dB console, we need:
    # slope = (0.7 - 0.5) / (-2.0 - (-24.7)) = 0.2 / 22.7 = 0.0088
    # To go from -2.0 dB to 0.0 dB: +2.0 dB
    # normalized = 0.7 + (2.0 * 0.0088) = 0.7176
    
    # But 0.7176 gave us -10.0 dB, so let me try a higher value
    # Let's try 0.75
    
    # For now, let's use a simple mapping based on our working data:
    # Scene file 0.0 dB should map to console 0.0 dB (unity gain)
    # Scene file +5.0 dB should map to console -7.5 dB
    
    # Let's try a direct mapping:
    if db_value <= -60:
        return 0.0
    elif db_value >= 10:
        return 1.0
    else:
        # Map scene dB to normalized using our calibration
        # 0.0 dB scene → 0.75 normalized (estimated for 0.0 dB console)
        # +5.0 dB scene → 0.563 normalized (known to give -7.5 dB console)
        
        # Calculate the slope
        scene_db1, normalized1 = 0.0, 0.75  # estimated for unity gain
        scene_db2, normalized2 = 5.0, 0.563  # known working value
        
        slope = (normalized2 - normalized1) / (scene_db2 - scene_db1)
        intercept = normalized1 - slope * scene_db1
        
        normalized = slope * db_value + intercept
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
    
    # Test 0.0 dB (unity gain) with refined calibration
    db_value = 0.0
    normalized = transform_db_to_x32_fader(db_value)
    
    print(f"🎚️  Refined calibration test: {db_value} dB → {normalized:.4f} normalized")
    print(f"🎯 Target: {ip_address}:{port}")
    print(f"🎯 Expected: 0.0 dB (unity gain) on console")
    
    success = send_osc_command(ip_address, port, "/ch/01/mix/fader", normalized)
    if success:
        print("✅ Refined calibrated fader command sent!")
    else:
        print("❌ Failed to send fader command")
    
    print("🎯 Test completed!")

if __name__ == "__main__":
    main() 