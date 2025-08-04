#!/usr/bin/env python3
"""
Test script to verify X32 OSC communication
"""

import socket
import struct
import sys
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

def send_osc_message(ip_address, port, address, *args):
    """Send OSC message to X32"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2)
        message = create_osc_message(address, *args)
        sock.sendto(message, (ip_address, port))
        sock.close()
        return True
    except Exception as e:
        print(f"Error sending OSC message: {e}")
        return False

def test_x32_commands(ip_address="192.168.1.100", port=10023):
    """Test various X32 OSC commands"""
    
    print(f"🧪 Testing X32 OSC commands at {ip_address}:{port}")
    print("=" * 50)
    
    # Test 1: Get console info
    print("1. Testing console info request...")
    if send_osc_message(ip_address, port, "/xinfo", ""):
        print("   ✅ Sent /xinfo command")
    else:
        print("   ❌ Failed to send /xinfo command")
    
    time.sleep(0.5)
    
    # Test 2: Set channel 1 fader to -20dB (should be very noticeable)
    print("2. Testing channel 1 fader control...")
    if send_osc_message(ip_address, port, "/ch/01/mix/fader", -20.0):
        print("   ✅ Sent fader command (should set channel 1 to -20dB)")
    else:
        print("   ❌ Failed to send fader command")
    
    time.sleep(1)
    
    # Test 3: Set channel 1 fader back to 0dB
    print("3. Restoring channel 1 fader...")
    if send_osc_message(ip_address, port, "/ch/01/mix/fader", 0.0):
        print("   ✅ Sent fader restore command (should set channel 1 to 0dB)")
    else:
        print("   ❌ Failed to send fader restore command")
    
    time.sleep(0.5)
    
    # Test 4: Toggle channel 1 mute (should be very visible)
    print("4. Testing channel 1 mute toggle...")
    if send_osc_message(ip_address, port, "/ch/01/mix/on", False):
        print("   ✅ Sent mute command (channel 1 should be muted)")
    else:
        print("   ❌ Failed to send mute command")
    
    time.sleep(2)
    
    # Test 5: Unmute channel 1
    print("5. Unmuting channel 1...")
    if send_osc_message(ip_address, port, "/ch/01/mix/on", True):
        print("   ✅ Sent unmute command (channel 1 should be unmuted)")
    else:
        print("   ❌ Failed to send unmute command")
    
    print("\n🎯 Test completed! Check your X32 console for:")
    print("   - Channel 1 fader moving to -20dB then back to 0dB")
    print("   - Channel 1 mute button toggling on/off")
    print("   - Any error messages on the X32 screen")

if __name__ == "__main__":
    ip_address = sys.argv[1] if len(sys.argv) > 1 else "192.168.1.100"
    test_x32_commands(ip_address, 10023) 