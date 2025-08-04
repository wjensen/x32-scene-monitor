#!/usr/bin/env python3
import socket

# X32 connection
ip = "192.168.1.116"
port = 10023

# Create OSC message for unmute
address = "/ch/01/mix/on"
message = address.encode('utf-8')
message += b'\x00' * (4 - len(message) % 4)  # Pad to 4-byte boundary
message += b',T\x00\x00'  # Type tag for True (unmute)

print(f"Sending unmute command to {ip}:{port}")
print(f"Address: {address}")

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message, (ip, port))
    sock.close()
    print("✅ Command sent successfully!")
    print("🎵 Will channel should now be unmuted")
except Exception as e:
    print(f"❌ Error: {e}") 