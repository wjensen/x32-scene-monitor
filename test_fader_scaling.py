#!/usr/bin/env python3
"""
Test different fader value ranges to find correct scaling
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
        
        message = create_osc_message(address, value)
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
    
    print("🧪 Testing different fader value ranges...")
    print(f"🎯 Target: {ip_address}:{port}")
    print("💡 Watch your X32 console - we need to find the right value range!")
    print()
    
    # Test different value ranges
    fader_tests = [
        ("1. Unity gain (0.0)", "/ch/01/mix/fader", 0.0),
        ("2. Half scale (0.5)", "/ch/01/mix/fader", 0.5),
        ("3. Full scale (1.0)", "/ch/01/mix/fader", 1.0),
        ("4. Negative (-0.5)", "/ch/01/mix/fader", -0.5),
        ("5. Small positive (0.1)", "/ch/01/mix/fader", 0.1),
        ("6. Small negative (-0.1)", "/ch/01/mix/fader", -0.1),
        ("7. dB scale (-20)", "/ch/01/mix/fader", -20.0),
        ("8. dB scale (0)", "/ch/01/mix/fader", 0.0),
        ("9. dB scale (+10)", "/ch/01/mix/fader", 10.0),
        ("10. Integer scale (50)", "/ch/01/mix/fader", 50),
        ("11. Integer scale (100)", "/ch/01/mix/fader", 100),
        ("12. Integer scale (0)", "/ch/01/mix/fader", 0),
    ]
    
    for name, address, value in fader_tests:
        print(f"🔧 {name}...")
        success = send_osc_command(ip_address, port, address, value)
        if success:
            print(f"✅ {name} command sent")
        else:
            print(f"❌ {name} command failed")
        print("⏳ Waiting 4 seconds... (watch your console!)")
        print()
        time.sleep(4)  # 4 second delay to see effects clearly
    
    print("🎯 All fader scaling tests completed!")
    print("💡 Tell me which value range worked correctly!")

if __name__ == "__main__":
    main() 