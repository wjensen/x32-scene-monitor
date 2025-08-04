#!/usr/bin/env python3
"""
Test different fader address variations for X32 - SLOW VERSION
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
    
    print("🧪 Testing different fader address variations - SLOW VERSION...")
    print(f"🎯 Target: {ip_address}:{port}")
    print("💡 Watch your X32 console - the fader should move!")
    print("⏰ Each test will wait 5 seconds so you can see the change clearly.")
    print()
    
    # Test different fader address variations
    fader_addresses = [
        ("1. Standard fader to 0dB", "/ch/01/mix/fader", 0.0),
        ("2. Standard fader to -20dB", "/ch/01/mix/fader", -20.0),
        ("3. Standard fader to +10dB", "/ch/01/mix/fader", 10.0),
        ("4. Integer fader to 0", "/ch/01/mix/fader", 0),
        ("5. Alternative fader to 0dB", "/ch/01/fader", 0.0),
        ("6. Alternative fader to -20dB", "/ch/01/fader", -20.0),
        ("7. Alternative fader to +10dB", "/ch/01/fader", 10.0),
        ("8. Level address to 0dB", "/ch/01/mix/level", 0.0),
        ("9. Level address to -20dB", "/ch/01/mix/level", -20.0),
        ("10. Level address to +10dB", "/ch/01/mix/level", 10.0),
        ("11. Simple level to 0dB", "/ch/01/level", 0.0),
        ("12. Simple level to -20dB", "/ch/01/level", -20.0),
        ("13. Simple level to +10dB", "/ch/01/level", 10.0),
    ]
    
    for name, address, value in fader_addresses:
        print(f"🔧 {name}...")
        success = send_osc_command(ip_address, port, address, value)
        if success:
            print(f"✅ {name} command sent")
        else:
            print(f"❌ {name} command failed")
        print("⏳ Waiting 5 seconds... (watch your console!)")
        print()
        time.sleep(5)  # 5 second delay to see effects clearly
    
    print("🎯 All fader address tests completed!")
    print("💡 Tell me which number worked!")

if __name__ == "__main__":
    main() 