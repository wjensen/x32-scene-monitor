#!/usr/bin/env python3
"""
Quick script to mute the "Will" channel on X32 console with detailed logging
"""

import socket
import struct
import sys
import time
import os
from datetime import datetime

def log_change(action, channel, address, value, ip_address, success=True):
    """Log changes to a file and print to console"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")
    
    # Log to file
    log_file = f"logs/x32_changes_{datetime.now().strftime('%Y%m%d')}.log"
    log_entry = f"[{timestamp}] {action}: Channel {channel} | Address: {address} | Value: {value} | IP: {ip_address} | Status: {'SUCCESS' if success else 'FAILED'}\n"
    
    try:
        with open(log_file, "a") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Warning: Could not write to log file: {e}")
    
    # Print to console
    status_icon = "✅" if success else "❌"
    print(f"{status_icon} [{timestamp}] {action}: Channel {channel} | {address} = {value}")

def create_osc_message(address, *args):
    """Create OSC message"""
    # OSC address
    message = address.encode('utf-8')
    message += b'\x00' * (4 - len(message) % 4)  # Pad to 4-byte boundary
    
    # OSC type tag string
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
    message += b'\x00' * (4 - len(type_tags) % 4)  # Pad to 4-byte boundary
    
    # OSC arguments
    for arg in args:
        if isinstance(arg, bool):
            pass  # No data for boolean
        elif isinstance(arg, int):
            message += struct.pack('>i', arg)
        elif isinstance(arg, float):
            message += struct.pack('>f', arg)
        elif isinstance(arg, str):
            message += arg.encode('utf-8')
            message += b'\x00' * (4 - len(arg.encode('utf-8')) % 4)  # Pad to 4-byte boundary
    
    return message

def test_connection(ip_address, port=10023, timeout=2):
    """Test if X32 console is reachable"""
    print(f"🔍 Testing connection to X32 at {ip_address}:{port}...")
    
    try:
        # Test basic socket connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(timeout)
        
        # Try to send a ping-like message
        test_message = create_osc_message("/xinfo", "")
        sock.sendto(test_message, (ip_address, port))
        
        # Try to receive a response (X32 might not respond to this, but we can test connectivity)
        try:
            sock.settimeout(1)
            data, addr = sock.recvfrom(1024)
            print(f"✅ Received response from {addr}")
            sock.close()
            return True
        except socket.timeout:
            # No response, but connection might still work
            print("⚠️  No response received, but connection may still work")
            sock.close()
            return True
            
    except socket.error as e:
        print(f"❌ Connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Connection test error: {e}")
        return False

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

def mute_channel(ip_address="192.168.1.116", port=10023, channel_name="Will"):
    """Mute a specific channel by name with logging"""
    
    # Test connection first
    if not test_connection(ip_address, port):
        print("❌ Cannot connect to X32 console. Please check:")
        print("   - X32 console is powered on")
        print("   - Network connection is working")
        print("   - IP address is correct")
        print("   - X32 is configured for OSC on port 10023")
        return False
    
    # Common channel mappings - you may need to adjust these
    channel_mappings = {
        "Will": "/ch/01/mix/on",  # Channel 1
        "Will1": "/ch/01/mix/on",
        "Will2": "/ch/02/mix/on", 
        "Will3": "/ch/03/mix/on",
        "Will4": "/ch/04/mix/on",
        "Will5": "/ch/05/mix/on",
        "Will6": "/ch/06/mix/on",
        "Will7": "/ch/07/mix/on",
        "Will8": "/ch/08/mix/on",
        "Will9": "/ch/09/mix/on",
        "Will10": "/ch/10/mix/on",
        "Will11": "/ch/11/mix/on",
        "Will12": "/ch/12/mix/on",
        "Will13": "/ch/13/mix/on",
        "Will14": "/ch/14/mix/on",
        "Will15": "/ch/15/mix/on",
        "Will16": "/ch/16/mix/on",
    }
    
    # Try exact match first
    if channel_name in channel_mappings:
        address = channel_mappings[channel_name]
        channel_num = channel_name.replace("Will", "")
        if not channel_num:
            channel_num = "1"
        
        print(f"🎛️  Muting {channel_name} at {address}")
        if send_osc_message(ip_address, port, address, False):
            log_change("MUTE", channel_num, address, False, ip_address, True)
            print(f"✅ Successfully sent mute command for {channel_name}")
            return True
        else:
            log_change("MUTE", channel_num, address, False, ip_address, False)
            print(f"❌ Failed to send mute command for {channel_name}")
            return False
    
    # Try numbered channels
    for i in range(1, 33):
        if f"Will{i}" == channel_name:
            address = f"/ch/{i:02d}/mix/on"
            print(f"🎛️  Muting {channel_name} at {address}")
            if send_osc_message(ip_address, port, address, False):
                log_change("MUTE", str(i), address, False, ip_address, True)
                print(f"✅ Successfully sent mute command for {channel_name}")
                return True
            else:
                log_change("MUTE", str(i), address, False, ip_address, False)
                print(f"❌ Failed to send mute command for {channel_name}")
                return False
    
    print(f"❌ Channel '{channel_name}' not found in mappings")
    print("Available mappings:")
    for name in channel_mappings.keys():
        print(f"  - {name}")
    return False

def unmute_channel(ip_address="192.168.1.116", port=10023, channel_name="Will"):
    """Unmute a specific channel by name with logging"""
    
    # Test connection first
    if not test_connection(ip_address, port):
        print("❌ Cannot connect to X32 console.")
        return False
    
    # Common channel mappings
    channel_mappings = {
        "Will": "/ch/01/mix/on",  # Channel 1
        "Will1": "/ch/01/mix/on",
        "Will2": "/ch/02/mix/on", 
        "Will3": "/ch/03/mix/on",
        "Will4": "/ch/04/mix/on",
        "Will5": "/ch/05/mix/on",
        "Will6": "/ch/06/mix/on",
        "Will7": "/ch/07/mix/on",
        "Will8": "/ch/08/mix/on",
        "Will9": "/ch/09/mix/on",
        "Will10": "/ch/10/mix/on",
        "Will11": "/ch/11/mix/on",
        "Will12": "/ch/12/mix/on",
        "Will13": "/ch/13/mix/on",
        "Will14": "/ch/14/mix/on",
        "Will15": "/ch/15/mix/on",
        "Will16": "/ch/16/mix/on",
    }
    
    # Try exact match first
    if channel_name in channel_mappings:
        address = channel_mappings[channel_name]
        channel_num = channel_name.replace("Will", "")
        if not channel_num:
            channel_num = "1"
        
        print(f"🎛️  Unmuting {channel_name} at {address}")
        if send_osc_message(ip_address, port, address, True):
            log_change("UNMUTE", channel_num, address, True, ip_address, True)
            print(f"✅ Successfully sent unmute command for {channel_name}")
            return True
        else:
            log_change("UNMUTE", channel_num, address, True, ip_address, False)
            print(f"❌ Failed to send unmute command for {channel_name}")
            return False
    
    # Try numbered channels
    for i in range(1, 33):
        if f"Will{i}" == channel_name:
            address = f"/ch/{i:02d}/mix/on"
            print(f"🎛️  Unmuting {channel_name} at {address}")
            if send_osc_message(ip_address, port, address, True):
                log_change("UNMUTE", str(i), address, True, ip_address, True)
                print(f"✅ Successfully sent unmute command for {channel_name}")
                return True
            else:
                log_change("UNMUTE", str(i), address, True, ip_address, False)
                print(f"❌ Failed to send unmute command for {channel_name}")
                return False
    
    print(f"❌ Channel '{channel_name}' not found in mappings")
    return False

if __name__ == "__main__":
    # Get arguments from command line
    if len(sys.argv) < 2:
        print("Usage: python3 mute_will.py [IP_ADDRESS] [CHANNEL_NAME] [ACTION]")
        print("Examples:")
        print("  python3 mute_will.py 192.168.1.116 Will1 mute")
        print("  python3 mute_will.py 192.168.1.116 Will1 unmute")
        print("  python3 mute_will.py 192.168.1.116 Will1")  # Defaults to mute
        sys.exit(1)
    
    ip_address = sys.argv[1] if len(sys.argv) > 1 else "192.168.1.116"
    channel_name = sys.argv[2] if len(sys.argv) > 2 else "Will1"
    action = sys.argv[3] if len(sys.argv) > 3 else "mute"
    
    print(f"🎯 Attempting to {action} '{channel_name}' on X32 at {ip_address}:10023")
    print("=" * 60)
    
    if action.lower() in ["mute", "m"]:
        mute_channel(ip_address, 10023, channel_name)
    elif action.lower() in ["unmute", "u", "un"]:
        unmute_channel(ip_address, 10023, channel_name)
    else:
        print(f"❌ Unknown action: {action}")
        print("Valid actions: mute, unmute") 