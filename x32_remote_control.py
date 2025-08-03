#!/usr/bin/env python3
"""
X32 Remote Control Application
Communicates with Behringer X32 over WiFi using OSC protocol
Similar functionality to X32-Edit
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import socket
import threading
import time
import json
from typing import Dict, Any, Optional
import queue
import struct

# OSC Protocol Implementation
class OSCMessage:
    def __init__(self, address: str, *args):
        self.address = address
        self.args = args
    
    def to_bytes(self) -> bytes:
        # Simplified OSC message format
        msg = self.address + '\0'
        msg += ',' + ''.join(['f' if isinstance(arg, float) else 'i' if isinstance(arg, int) else 's' for arg in self.args]) + '\0'
        for arg in self.args:
            if isinstance(arg, str):
                msg += arg + '\0'
            elif isinstance(arg, (int, float)):
                msg += struct.pack('>f' if isinstance(arg, float) else '>i', arg)
        return msg.encode('utf-8')

class X32Connection:
    def __init__(self, ip_address: str = "192.168.1.100", port: int = 10023):
        self.ip_address = ip_address
        self.port = port
        self.socket = None
        self.connected = False
        self.message_queue = queue.Queue()
        self.response_queue = queue.Queue()
        
    def connect(self) -> bool:
        """Connect to X32"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(1.0)
            self.connected = True
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from X32"""
        if self.socket:
            self.socket.close()
        self.connected = False
    
    def send_message(self, address: str, *args):
        """Send OSC message to X32"""
        if not self.connected:
            return False
        
        try:
            msg = OSCMessage(address, *args)
            self.socket.sendto(msg.to_bytes(), (self.ip_address, self.port))
            return True
        except Exception as e:
            print(f"Send failed: {e}")
            return False
    
    def send_fader_level(self, channel: int, level: float):
        """Send fader level for a channel"""
        address = f"/ch/{channel:02d}/mix/fader"
        return self.send_message(address, level)
    
    def send_bus_fader_level(self, bus: int, level: float):
        """Send fader level for a bus"""
        address = f"/bus/{bus:02d}/mix/fader"
        return self.send_message(address, level)
    
    def send_main_fader_level(self, level: float):
        """Send main stereo fader level"""
        address = "/main/st/mix/fader"
        return self.send_message(address, level)
    
    def send_channel_mute(self, channel: int, mute: bool):
        """Send channel mute state"""
        address = f"/ch/{channel:02d}/mix/on"
        return self.send_message(address, 0 if mute else 1)
    
    def send_bus_mute(self, bus: int, mute: bool):
        """Send bus mute state"""
        address = f"/bus/{bus:02d}/mix/on"
        return self.send_message(address, 0 if mute else 1)
    
    def send_channel_name(self, channel: int, name: str):
        """Send channel name"""
        address = f"/ch/{channel:02d}/config/name"
        return self.send_message(address, name)
    
    def send_bus_name(self, bus: int, name: str):
        """Send bus name"""
        address = f"/bus/{bus:02d}/config/name"
        return self.send_message(address, name)

class X32RemoteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("X32 Remote Control")
        self.root.geometry("1200x800")
        
        # X32 Connection
        self.x32 = X32Connection()
        
        # GUI Variables
        self.connection_var = tk.StringVar(value="Disconnected")
        self.ip_var = tk.StringVar(value="192.168.1.100")
        self.port_var = tk.IntVar(value=10023)
        
        self.setup_gui()
        
    def setup_gui(self):
        """Setup the GUI interface"""
        # Connection Frame
        conn_frame = ttk.LabelFrame(self.root, text="Connection", padding="10")
        conn_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        ttk.Label(conn_frame, text="IP Address:").grid(row=0, column=0, sticky="w")
        ttk.Entry(conn_frame, textvariable=self.ip_var, width=15).grid(row=0, column=1, padx=5)
        
        ttk.Label(conn_frame, text="Port:").grid(row=0, column=2, sticky="w", padx=(10,0))
        ttk.Entry(conn_frame, textvariable=self.port_var, width=8).grid(row=0, column=3, padx=5)
        
        self.connect_btn = ttk.Button(conn_frame, text="Connect", command=self.toggle_connection)
        self.connect_btn.grid(row=0, column=4, padx=10)
        
        ttk.Label(conn_frame, textvariable=self.connection_var).grid(row=0, column=5, padx=10)
        
        # Main Control Frame
        main_frame = ttk.Frame(self.root)
        main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        # Channel Faders
        self.setup_channel_faders(main_frame)
        
        # Bus Faders
        self.setup_bus_faders(main_frame)
        
        # Main Fader
        self.setup_main_fader(main_frame)
        
        # Configuration
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
    def setup_channel_faders(self, parent):
        """Setup channel fader controls"""
        ch_frame = ttk.LabelFrame(parent, text="Channel Faders", padding="10")
        ch_frame.grid(row=0, column=0, sticky="nsew", padx=(0,5))
        
        # Channel fader variables
        self.ch_faders = {}
        self.ch_mutes = {}
        self.ch_names = {}
        
        # Create channel controls
        for i in range(8):  # First 8 channels
            ch_num = i + 1
            
            # Channel name
            name_var = tk.StringVar(value=f"Ch{ch_num}")
            self.ch_names[ch_num] = name_var
            ttk.Entry(ch_frame, textvariable=name_var, width=8).grid(row=i, column=0, padx=2, pady=1)
            
            # Fader
            fader_var = tk.DoubleVar(value=0.0)
            self.ch_faders[ch_num] = fader_var
            fader = ttk.Scale(ch_frame, from_=-60, to=10, variable=fader_var, 
                            orient="vertical", length=150,
                            command=lambda val, ch=ch_num: self.on_channel_fader_change(ch, float(val)))
            fader.grid(row=i, column=1, padx=2, pady=1)
            
            # Fader value label
            fader_label = ttk.Label(ch_frame, text="0.0")
            fader_label.grid(row=i, column=2, padx=2, pady=1)
            
            # Mute button
            mute_var = tk.BooleanVar()
            self.ch_mutes[ch_num] = mute_var
            mute_btn = ttk.Checkbutton(ch_frame, text="M", variable=mute_var,
                                     command=lambda ch=ch_num: self.on_channel_mute_change(ch))
            mute_btn.grid(row=i, column=3, padx=2, pady=1)
        
        ch_frame.grid_columnconfigure(1, weight=1)
        
    def setup_bus_faders(self, parent):
        """Setup bus fader controls"""
        bus_frame = ttk.LabelFrame(parent, text="Bus Faders", padding="10")
        bus_frame.grid(row=0, column=1, sticky="nsew", padx=(5,0))
        
        # Bus fader variables
        self.bus_faders = {}
        self.bus_mutes = {}
        self.bus_names = {}
        
        # Create bus controls
        for i in range(8):  # First 8 buses
            bus_num = i + 1
            
            # Bus name
            name_var = tk.StringVar(value=f"Bus{bus_num}")
            self.bus_names[bus_num] = name_var
            ttk.Entry(bus_frame, textvariable=name_var, width=8).grid(row=i, column=0, padx=2, pady=1)
            
            # Fader
            fader_var = tk.DoubleVar(value=0.0)
            self.bus_faders[bus_num] = fader_var
            fader = ttk.Scale(bus_frame, from_=-60, to=10, variable=fader_var,
                            orient="vertical", length=150,
                            command=lambda val, bus=bus_num: self.on_bus_fader_change(bus, float(val)))
            fader.grid(row=i, column=1, padx=2, pady=1)
            
            # Fader value label
            fader_label = ttk.Label(bus_frame, text="0.0")
            fader_label.grid(row=i, column=2, padx=2, pady=1)
            
            # Mute button
            mute_var = tk.BooleanVar()
            self.bus_mutes[bus_num] = mute_var
            mute_btn = ttk.Checkbutton(bus_frame, text="M", variable=mute_var,
                                     command=lambda bus=bus_num: self.on_bus_mute_change(bus))
            mute_btn.grid(row=i, column=3, padx=2, pady=1)
        
        bus_frame.grid_columnconfigure(1, weight=1)
        
    def setup_main_fader(self, parent):
        """Setup main stereo fader control"""
        main_frame = ttk.LabelFrame(parent, text="Main Stereo", padding="10")
        main_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10,0))
        
        # Main fader
        self.main_fader_var = tk.DoubleVar(value=0.0)
        main_fader = ttk.Scale(main_frame, from_=-60, to=10, variable=self.main_fader_var,
                              orient="horizontal", length=400,
                              command=lambda val: self.on_main_fader_change(float(val)))
        main_fader.grid(row=0, column=0, padx=10, pady=5)
        
        # Main fader value label
        self.main_fader_label = ttk.Label(main_frame, text="0.0 dB")
        self.main_fader_label.grid(row=0, column=1, padx=10, pady=5)
        
        # Main mute button
        self.main_mute_var = tk.BooleanVar()
        main_mute_btn = ttk.Checkbutton(main_frame, text="Main Mute", variable=self.main_mute_var,
                                       command=self.on_main_mute_change)
        main_mute_btn.grid(row=0, column=2, padx=10, pady=5)
        
    def toggle_connection(self):
        """Toggle X32 connection"""
        if not self.x32.connected:
            # Connect
            self.x32.ip_address = self.ip_var.get()
            self.x32.port = self.port_var.get()
            
            if self.x32.connect():
                self.connection_var.set("Connected")
                self.connect_btn.config(text="Disconnect")
                messagebox.showinfo("Success", "Connected to X32!")
            else:
                messagebox.showerror("Error", "Failed to connect to X32")
        else:
            # Disconnect
            self.x32.disconnect()
            self.connection_var.set("Disconnected")
            self.connect_btn.config(text="Connect")
            messagebox.showinfo("Info", "Disconnected from X32")
    
    def on_channel_fader_change(self, channel: int, value: float):
        """Handle channel fader change"""
        if self.x32.connected:
            self.x32.send_fader_level(channel, value)
    
    def on_bus_fader_change(self, bus: int, value: float):
        """Handle bus fader change"""
        if self.x32.connected:
            self.x32.send_bus_fader_level(bus, value)
    
    def on_main_fader_change(self, value: float):
        """Handle main fader change"""
        if self.x32.connected:
            self.x32.send_main_fader_level(value)
            self.main_fader_label.config(text=f"{value:.1f} dB")
    
    def on_channel_mute_change(self, channel: int):
        """Handle channel mute change"""
        if self.x32.connected:
            mute = self.ch_mutes[channel].get()
            self.x32.send_channel_mute(channel, mute)
    
    def on_bus_mute_change(self, bus: int):
        """Handle bus mute change"""
        if self.x32.connected:
            mute = self.bus_mutes[bus].get()
            self.x32.send_bus_mute(bus, mute)
    
    def on_main_mute_change(self):
        """Handle main mute change"""
        if self.x32.connected:
            mute = self.main_mute_var.get()
            # Main mute would be implemented here
            pass

def main():
    root = tk.Tk()
    app = X32RemoteApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 