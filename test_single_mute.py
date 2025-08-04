#!/usr/bin/env python3
"""
Test mute commands one by one
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
    
    print("🧪 Testing mute commands one by one...")
    print(f"🎯 Target: {ip_address}:{port}")
    print("💡 Watch your X32 console and tell me which one works!")
    print()
    
    # Test different mute address variations
    mute_addresses = [
        ("1. Standard mute OFF", "/ch/01/mix/on", False),
        ("2. Standard mute ON", "/ch/01/mix/on", True),
        ("3. Integer mute OFF", "/ch/01/mix/on", 0),
        ("4. Integer mute ON", "/ch/01/mix/on", 1),
        ("5. Alternative mute OFF", "/ch/01/mix/mute", False),
        ("6. Alternative mute ON", "/ch/01/mix/mute", True),
        ("7. Integer alt mute OFF", "/ch/01/mix/mute", 0),
        ("8. Integer alt mute ON", "/ch/01/mix/mute", 1),
        ("9. Simple mute OFF", "/ch/01/mute", False),
        ("10. Simple mute ON", "/ch/01/mute", True),
    ]
    
    for name, address, value in mute_addresses:
        print(f"🔧 {name}...")
        success = send_osc_command(ip_address, port, address, value)
        if success:
            print(f"✅ {name} command sent")
        else:
            print(f"❌ {name} command failed")
        print("⏳ Waiting 3 seconds... (watch your console!)")
        print()
        time.sleep(3)  # 3 second delay to see effects
    
    print("🎯 All mute tests completed!")
    print("💡 Tell me which number worked!")

if __name__ == "__main__":
    main() 