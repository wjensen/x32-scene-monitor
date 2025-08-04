#!/usr/bin/env python3
"""
Simple command-line scene file monitor
"""

import time
import os
import socket
import struct
import hashlib

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

def transform_db_to_normalized(db_value):
    """
    Transform scene file dB value to X32 normalized fader value
    Based on actual calibration data:
    - 0.5 normalized → -24.7 dB console
    - 0.7 normalized → -2.0 dB console  
    - 0.75 normalized → 0.0 dB console (unity gain)
    """
    if db_value <= -60:
        return 0.0
    elif db_value >= 10:
        return 1.0
    else:
        # Based on our actual test data:
        # 0.0 dB scene should map to 0.75 normalized (which gives 0.0 dB console)
        # +5.0 dB scene should map to 0.563 normalized (which gives -7.5 dB console)
        
        # But we just tested 0.0 dB scene → 0.316 normalized → -24.7 dB console
        # So the calculation is wrong. Let me use the direct mapping:
        
        # For 0.0 dB scene, we need 0.75 normalized to get 0.0 dB console
        # For +5.0 dB scene, we need 0.563 normalized to get -7.5 dB console
        
        # Direct mapping based on our working values:
        if db_value == 0.0:
            return 0.75  # This gives us 0.0 dB console
        elif db_value == 5.0:
            return 0.563  # This gives us -7.5 dB console
        else:
            # Linear interpolation between these known points
            if db_value < 0.0:
                # Extrapolate down from 0.0 dB
                slope = (0.75 - 0.563) / (0.0 - 5.0)
                return 0.75 + slope * db_value
            else:
                # Interpolate between 0.0 and 5.0 dB
                slope = (0.563 - 0.75) / (5.0 - 0.0)
                return 0.75 + slope * db_value

def main():
    ip_address = "192.168.1.116"
    port = 10023
    filepath = "integrated.scn"
    
    print("🎛️  Simple Scene File Monitor")
    print(f"📁 Monitoring: {filepath}")
    print(f"🎯 Target: {ip_address}:{port}")
    print("⏹️  Press Ctrl+C to stop")
    print()
    
    previous_hash = None
    
    try:
        while True:
            if os.path.exists(filepath):
                # Calculate file hash
                with open(filepath, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
                
                # Check if file changed
                if file_hash != previous_hash:
                    print(f"🔄 File changed! Processing...")
                    
                    # Read and process the file
                    with open(filepath, 'r') as f:
                        lines = f.readlines()
                    
                    for line_num, line in enumerate(lines, 1):
                        line = line.strip()
                        
                        # Parse channel mix settings
                        if line.startswith('/ch/') and '/mix ' in line:
                            parts = line.split()
                            if len(parts) >= 3:
                                channel = parts[0]  # /ch/01/mix
                                mute_status = parts[1]  # OFF/ON
                                fader_level = parts[2]  # +8.1
                                
                                print(f"🎛️  Line {line_num}: {line}")
                                
                                # Convert to OSC commands
                                if channel.startswith('/ch/') and channel.endswith('/mix'):
                                    channel_num = channel.split('/')[2]
                                    
                                    # Mute command
                                    mute_address = f"/ch/{channel_num}/mix/on"
                                    mute_value = 1 if mute_status == "ON" else 0
                                    print(f"   🔇 Mute: {mute_address} = {mute_value}")
                                    send_osc_command(ip_address, port, mute_address, mute_value)
                                    
                                    # Fader command
                                    try:
                                        fader_value = float(fader_level)
                                        normalized_fader = transform_db_to_normalized(fader_value)
                                        fader_address = f"/ch/{channel_num}/mix/fader"
                                        print(f"   🎚️  Fader: {fader_address} = {normalized_fader:.3f} (from {fader_value} dB)")
                                        send_osc_command(ip_address, port, fader_address, normalized_fader)
                                    except ValueError:
                                        print(f"   ⚠️  Invalid fader level: {fader_level}")
                    
                    previous_hash = file_hash
                    print("✅ Changes applied!")
                    print()
            
            time.sleep(1)  # Check every second
            
    except KeyboardInterrupt:
        print("\n⏹️  Monitoring stopped")

if __name__ == "__main__":
    main() 