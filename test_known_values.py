#!/usr/bin/env python3
"""
Test known working fader values
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
    
    # Test the exact values that worked before
    test_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    
    print(f"🎚️  Testing known normalized values")
    print(f"🎯 Target: {ip_address}:{port}")
    print()
    
    for i, value in enumerate(test_values):
        print(f"Test {i+1}: Sending {value:.1f}")
        success = send_osc_command(ip_address, port, "/ch/01/mix/fader", value)
        if success:
            print(f"✅ Sent {value:.1f}")
        else:
            print(f"❌ Failed to send {value:.1f}")
        
        # Ask user what position the fader moved to
        input(f"🎚️  What position is the fader at now? (press Enter when ready for next test)")
    
    print("🎯 All tests completed!")

if __name__ == "__main__":
    main() 