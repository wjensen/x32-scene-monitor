#!/usr/bin/env python3
"""
Direct OSC command to unmute Will channel
"""

import socket
import struct

def send_unmute_command():
    """Send unmute command directly to X32"""
    
    # X32 connection details
    ip_address = "192.168.1.116"
    port = 10023
    
    # OSC message details
    address = "/ch/01/mix/on"
    value = True  # True = unmute, False = mute
    
    print(f"🎛️  Sending direct command to X32")
    print(f"IP: {ip_address}:{port}")
    print(f"Address: {address}")
    print(f"Value: {value} (unmute)")
    print("=" * 40)
    
    try:
        # Create socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2)
        
        # Create OSC message
        message = address.encode('utf-8')
        message += b'\x00' * (4 - len(message) % 4)
        
        # Add type tag
        type_tag = ',T'  # T = True (boolean)
        message += type_tag.encode('utf-8')
        message += b'\x00' * (4 - len(type_tag) % 4)
        
        # Send message
        sock.sendto(message, (ip_address, port))
        sock.close()
        
        print("✅ OSC command sent successfully!")
        print("🎵 Will channel should now be unmuted")
        return True
        
    except Exception as e:
        print(f"❌ Error sending command: {e}")
        return False

if __name__ == "__main__":
    send_unmute_command() 