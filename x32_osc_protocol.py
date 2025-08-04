#!/usr/bin/env python3
"""
X32 OSC Protocol Implementation
Based on official X32-OSC specifications

This module implements the complete X32 OSC protocol for:
- Channel control (/ch)
- Bus control (/bus) 
- Main stereo control (/main/st)
- Effects control (/fx)
- Metering (/meters)
- Scene management (/show, /load, /save)
- And more...

Author: AI Assistant
Based on: X32-OSC.pdf specifications
"""

import socket
import struct
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import json
from typing import Dict, List, Any, Optional, Callable
import queue

class X32OSCMessage:
    """Proper OSC message implementation for X32"""
    
    def __init__(self, address: str, *args):
        self.address = address
        self.args = args
        self.types = self._get_type_tags(args)
    
    def _get_type_tags(self, args) -> str:
        """Generate OSC type tags string"""
        type_tags = ","
        for arg in args:
            if isinstance(arg, str):
                type_tags += "s"
            elif isinstance(arg, int):
                type_tags += "i"
            elif isinstance(arg, float):
                type_tags += "f"
            elif isinstance(arg, bytes):
                type_tags += "b"
            else:
                type_tags += "s"  # Default to string
        return type_tags
    
    def to_bytes(self) -> bytes:
        """Convert OSC message to bytes"""
        # OSC address pattern (null-padded to 4-byte boundary)
        address_bytes = self.address.encode('utf-8')
        address_padding = (4 - (len(address_bytes) % 4)) % 4
        address_data = address_bytes + b'\x00' * address_padding
        
        # OSC type tags (null-padded to 4-byte boundary)
        types_bytes = self.types.encode('utf-8')
        types_padding = (4 - (len(types_bytes) % 4)) % 4
        types_data = types_bytes + b'\x00' * types_padding
        
        # OSC arguments
        args_data = b''
        for arg in self.args:
            if isinstance(arg, str):
                arg_bytes = arg.encode('utf-8')
                arg_padding = (4 - (len(arg_bytes) % 4)) % 4
                args_data += arg_bytes + b'\x00' * arg_padding
            elif isinstance(arg, int):
                args_data += struct.pack('>i', arg)
            elif isinstance(arg, float):
                args_data += struct.pack('>f', arg)
            elif isinstance(arg, bytes):
                # Blob: 4-byte size + data + padding
                size = len(arg)
                args_data += struct.pack('>i', size)
                blob_padding = (4 - (size % 4)) % 4
                args_data += arg + b'\x00' * blob_padding
        
        return address_data + types_data + args_data

class X32OSCConnection:
    """X32 OSC connection with proper protocol implementation"""
    
    def __init__(self, ip_address: str = "192.168.1.100", port: int = 10023):
        self.ip_address = ip_address
        self.port = port
        self.socket = None
        self.connected = False
        self.listen_thread = None
        self.running = False
        self.callbacks = {}
        self.meter_data = {}
        
    def connect(self) -> bool:
        """Connect to X32 console"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(1.0)
            self.connected = True
            
            # Start listening thread
            self.running = True
            self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.listen_thread.start()
            
            # Get console info
            self.send_message("/info")
            return True
            
        except Exception as e:
            print(f"Connection failed: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from X32 console"""
        self.running = False
        self.connected = False
        if self.socket:
            self.socket.close()
            self.socket = None
    
    def send_message(self, address: str, *args):
        """Send OSC message to X32"""
        if not self.connected:
            return False
        
        try:
            message = X32OSCMessage(address, *args)
            data = message.to_bytes()
            self.socket.sendto(data, (self.ip_address, self.port))
            return True
        except Exception as e:
            print(f"Send failed: {e}")
            return False
    
    def _listen_loop(self):
        """Listen for OSC messages from X32"""
        while self.running and self.connected:
            try:
                data, addr = self.socket.recvfrom(4096)
                self._parse_osc_message(data)
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"Listen error: {e}")
    
    def _parse_osc_message(self, data: bytes):
        """Parse incoming OSC message"""
        try:
            # Parse address
            null_pos = data.find(b'\x00')
            if null_pos == -1:
                return
            
            address = data[:null_pos].decode('utf-8')
            data = data[null_pos:]
            
            # Find type tags
            while data and data[0] == 0:
                data = data[1:]
            
            if not data:
                return
            
            null_pos = data.find(b'\x00')
            if null_pos == -1:
                return
            
            type_tags = data[:null_pos].decode('utf-8')
            data = data[null_pos:]
            
            # Skip padding
            while data and data[0] == 0:
                data = data[1:]
            
            # Parse arguments
            args = []
            for tag in type_tags[1:]:  # Skip comma
                if tag == 's':  # String
                    null_pos = data.find(b'\x00')
                    if null_pos == -1:
                        break
                    args.append(data[:null_pos].decode('utf-8'))
                    data = data[null_pos:]
                    # Skip padding
                    while data and data[0] == 0:
                        data = data[1:]
                elif tag == 'i':  # Integer
                    if len(data) >= 4:
                        args.append(struct.unpack('>i', data[:4])[0])
                        data = data[4:]
                elif tag == 'f':  # Float
                    if len(data) >= 4:
                        args.append(struct.unpack('>f', data[:4])[0])
                        data = data[4:]
                elif tag == 'b':  # Blob
                    if len(data) >= 4:
                        size = struct.unpack('>i', data[:4])[0]
                        data = data[4:]
                        if len(data) >= size:
                            args.append(data[:size])
                            data = data[size:]
                            # Skip padding
                            while data and data[0] == 0:
                                data = data[1:]
            
            # Handle the message
            self._handle_message(address, args)
            
        except Exception as e:
            print(f"Parse error: {e}")
    
    def _handle_message(self, address: str, args: List[Any]):
        """Handle parsed OSC message"""
        # Handle meter data
        if address == "/meters":
            if args and isinstance(args[0], bytes):
                self._parse_meter_data(args[0])
        
        # Handle info response
        elif address == "/info":
            print(f"X32 Info: {args}")
        
        # Handle status updates
        elif address.startswith("/-stat/"):
            print(f"Status: {address} = {args}")
        
        # Call registered callbacks
        if address in self.callbacks:
            for callback in self.callbacks[address]:
                try:
                    callback(address, args)
                except Exception as e:
                    print(f"Callback error: {e}")
    
    def _parse_meter_data(self, data: bytes):
        """Parse meter data blob"""
        try:
            # Parse 96 float values (32 input + 32 gate + 32 dynamic)
            if len(data) >= 96 * 4:
                values = struct.unpack('>96f', data[:96*4])
                
                # Organize meter data
                self.meter_data = {
                    'input': values[:32],
                    'gate': values[32:64],
                    'dynamic': values[64:96]
                }
        except Exception as e:
            print(f"Meter parse error: {e}")
    
    def register_callback(self, address: str, callback: Callable):
        """Register callback for specific OSC address"""
        if address not in self.callbacks:
            self.callbacks[address] = []
        self.callbacks[address].append(callback)
    
    # Channel Control Methods
    def set_channel_fader(self, channel: int, level: float):
        """Set channel fader level (0.0 to 1.0)"""
        address = f"/ch/{channel:02d}/mix/fader"
        return self.send_message(address, level)
    
    def get_channel_fader(self, channel: int):
        """Get channel fader level"""
        address = f"/ch/{channel:02d}/mix/fader"
        return self.send_message(address)
    
    def set_channel_mute(self, channel: int, mute: bool):
        """Set channel mute state"""
        address = f"/ch/{channel:02d}/mix/on"
        value = "ON" if not mute else "OFF"
        return self.send_message(address, value)
    
    def set_channel_name(self, channel: int, name: str):
        """Set channel name"""
        address = f"/ch/{channel:02d}/config/name"
        return self.send_message(address, name)
    
    def set_channel_pan(self, channel: int, pan: float):
        """Set channel pan (-1.0 to 1.0)"""
        address = f"/ch/{channel:02d}/mix/pan"
        return self.send_message(address, pan)
    
    # Bus Control Methods
    def set_bus_fader(self, bus: int, level: float):
        """Set bus fader level"""
        address = f"/bus/{bus:02d}/mix/fader"
        return self.send_message(address, level)
    
    def set_bus_mute(self, bus: int, mute: bool):
        """Set bus mute state"""
        address = f"/bus/{bus:02d}/mix/on"
        value = "ON" if not mute else "OFF"
        return self.send_message(address, value)
    
    def set_bus_name(self, bus: int, name: str):
        """Set bus name"""
        address = f"/bus/{bus:02d}/config/name"
        return self.send_message(address, name)
    
    # Main Stereo Control
    def set_main_fader(self, level: float):
        """Set main stereo fader level"""
        address = "/main/st/mix/fader"
        return self.send_message(address, level)
    
    def set_main_mute(self, mute: bool):
        """Set main stereo mute"""
        address = "/main/st/mix/on"
        value = "ON" if not mute else "OFF"
        return self.send_message(address, value)
    
    # Effects Control
    def set_fx_type(self, fx: int, fx_type: str):
        """Set effects type"""
        address = f"/fx/{fx}/config/type"
        return self.send_message(address, fx_type)
    
    def set_fx_param(self, fx: int, param: str, value: float):
        """Set effects parameter"""
        address = f"/fx/{fx}/par/{param}"
        return self.send_message(address, value)
    
    # Metering
    def start_meters(self, meter_type: str = "meters/1"):
        """Start meter data streaming"""
        return self.send_message("/meters", meter_type)
    
    def stop_meters(self):
        """Stop meter data streaming"""
        return self.send_message("/meters", "")
    
    # Scene Management
    def load_scene(self, scene_number: int):
        """Load scene by number"""
        return self.send_message("/-action/loadscene", scene_number)
    
    def save_scene(self, scene_number: int, name: str):
        """Save scene"""
        return self.send_message("/-action/savescene", scene_number, name)
    
    def get_scene_list(self):
        """Get list of scenes"""
        return self.send_message("/-show/scenes")
    
    # Remote Control
    def start_remote(self):
        """Start remote control mode"""
        return self.send_message("/xremote")
    
    def stop_remote(self):
        """Stop remote control mode"""
        return self.send_message("/xremote", "")

class X32OSCApp:
    """Enhanced X32 OSC Control Application"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("X32 OSC Protocol Control")
        self.root.geometry("1200x800")
        
        self.connection = X32OSCConnection()
        self.setup_gui()
        
    def setup_gui(self):
        """Setup the GUI"""
        # Connection frame
        conn_frame = ttk.LabelFrame(self.root, text="Connection", padding="10")
        conn_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        ttk.Label(conn_frame, text="IP Address:").grid(row=0, column=0, sticky="w")
        self.ip_var = tk.StringVar(value="192.168.1.100")
        ttk.Entry(conn_frame, textvariable=self.ip_var, width=15).grid(row=0, column=1, padx=5)
        
        ttk.Label(conn_frame, text="Port:").grid(row=0, column=2, sticky="w")
        self.port_var = tk.StringVar(value="10023")
        ttk.Entry(conn_frame, textvariable=self.port_var, width=8).grid(row=0, column=3, padx=5)
        
        self.connect_btn = ttk.Button(conn_frame, text="Connect", command=self.toggle_connection)
        self.connect_btn.grid(row=0, column=4, padx=10)
        
        # Status
        self.status_var = tk.StringVar(value="Disconnected")
        ttk.Label(conn_frame, textvariable=self.status_var).grid(row=0, column=5, padx=10)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)
        
        # Setup tabs
        self.setup_faders_tab()
        self.setup_meters_tab()
        self.setup_scenes_tab()
        self.setup_effects_tab()
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        
    def setup_faders_tab(self):
        """Setup faders control tab"""
        faders_frame = ttk.Frame(self.notebook)
        self.notebook.add(faders_frame, text="Faders")
        
        # Channels frame
        ch_frame = ttk.LabelFrame(faders_frame, text="Channels", padding="10")
        ch_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        self.ch_faders = {}
        self.ch_mutes = {}
        self.ch_names = {}
        
        for i in range(32):
            row = i // 8
            col = i % 8
            
            # Channel name
            name_var = tk.StringVar(value=f"Ch{i+1}")
            name_entry = ttk.Entry(ch_frame, textvariable=name_var, width=8)
            name_entry.grid(row=row*3, column=col, padx=2, pady=1)
            self.ch_names[i+1] = name_var
            
            # Fader
            fader_var = tk.DoubleVar(value=0.0)
            fader = ttk.Scale(ch_frame, from_=0.0, to=1.0, variable=fader_var, 
                            orient="vertical", length=100,
                            command=lambda v, ch=i+1: self.on_ch_fader_change(ch, float(v)))
            fader.grid(row=row*3+1, column=col, padx=2, pady=1)
            self.ch_faders[i+1] = fader_var
            
            # Mute button
            mute_var = tk.BooleanVar()
            mute_btn = ttk.Checkbutton(ch_frame, text="M", variable=mute_var,
                                     command=lambda ch=i+1, var=mute_var: self.on_ch_mute_change(ch, var.get()))
            mute_btn.grid(row=row*3+2, column=col, padx=2, pady=1)
            self.ch_mutes[i+1] = mute_var
        
        # Buses frame
        bus_frame = ttk.LabelFrame(faders_frame, text="Buses", padding="10")
        bus_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        self.bus_faders = {}
        self.bus_mutes = {}
        
        for i in range(16):
            row = i // 4
            col = i % 4
            
            # Bus name
            ttk.Label(bus_frame, text=f"Bus{i+1}").grid(row=row*3, column=col, padx=2, pady=1)
            
            # Fader
            fader_var = tk.DoubleVar(value=0.0)
            fader = ttk.Scale(bus_frame, from_=0.0, to=1.0, variable=fader_var,
                            orient="vertical", length=100,
                            command=lambda v, bus=i+1: self.on_bus_fader_change(bus, float(v)))
            fader.grid(row=row*3+1, column=col, padx=2, pady=1)
            self.bus_faders[i+1] = fader_var
            
            # Mute button
            mute_var = tk.BooleanVar()
            mute_btn = ttk.Checkbutton(bus_frame, text="M", variable=mute_var,
                                     command=lambda bus=i+1, var=mute_var: self.on_bus_mute_change(bus, var.get()))
            mute_btn.grid(row=row*3+2, column=col, padx=2, pady=1)
            self.bus_mutes[i+1] = mute_var
        
        # Main frame
        main_frame = ttk.LabelFrame(faders_frame, text="Main Stereo", padding="10")
        main_frame.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
        
        # Main fader
        self.main_fader_var = tk.DoubleVar(value=0.0)
        main_fader = ttk.Scale(main_frame, from_=0.0, to=1.0, variable=self.main_fader_var,
                              orient="vertical", length=150,
                              command=lambda v: self.on_main_fader_change(float(v)))
        main_fader.grid(row=0, column=0, padx=10, pady=5)
        
        # Main mute
        self.main_mute_var = tk.BooleanVar()
        main_mute = ttk.Checkbutton(main_frame, text="Main Mute", variable=self.main_mute_var,
                                   command=lambda: self.on_main_mute_change(self.main_mute_var.get()))
        main_mute.grid(row=1, column=0, padx=10, pady=5)
        
        # Configure grid weights
        faders_frame.columnconfigure(0, weight=1)
        faders_frame.columnconfigure(1, weight=1)
        faders_frame.columnconfigure(2, weight=1)
        
    def setup_meters_tab(self):
        """Setup meters display tab"""
        meters_frame = ttk.Frame(self.notebook)
        self.notebook.add(meters_frame, text="Meters")
        
        # Meter controls
        controls_frame = ttk.Frame(meters_frame)
        controls_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        ttk.Button(controls_frame, text="Start Meters", command=self.start_meters).grid(row=0, column=0, padx=5)
        ttk.Button(controls_frame, text="Stop Meters", command=self.stop_meters).grid(row=0, column=1, padx=5)
        
        # Meter display
        self.meter_canvas = tk.Canvas(meters_frame, width=800, height=400, bg="black")
        self.meter_canvas.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        # Configure grid weights
        meters_frame.columnconfigure(0, weight=1)
        meters_frame.rowconfigure(1, weight=1)
        
    def setup_scenes_tab(self):
        """Setup scene management tab"""
        scenes_frame = ttk.Frame(self.notebook)
        self.notebook.add(scenes_frame, text="Scenes")
        
        # Scene controls
        controls_frame = ttk.Frame(scenes_frame)
        controls_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        ttk.Button(controls_frame, text="Load Scene List", command=self.load_scene_list).grid(row=0, column=0, padx=5)
        ttk.Button(controls_frame, text="Start Remote", command=self.start_remote).grid(row=0, column=1, padx=5)
        ttk.Button(controls_frame, text="Stop Remote", command=self.stop_remote).grid(row=0, column=2, padx=5)
        
        # Scene list
        list_frame = ttk.LabelFrame(scenes_frame, text="Scenes", padding="10")
        list_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        self.scene_listbox = tk.Listbox(list_frame, height=15)
        self.scene_listbox.grid(row=0, column=0, sticky="nsew")
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.scene_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.scene_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Scene actions
        actions_frame = ttk.Frame(scenes_frame)
        actions_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        
        ttk.Button(actions_frame, text="Load Selected", command=self.load_selected_scene).grid(row=0, column=0, padx=5)
        ttk.Button(actions_frame, text="Save Scene", command=self.save_scene_dialog).grid(row=0, column=1, padx=5)
        
        # Configure grid weights
        scenes_frame.columnconfigure(0, weight=1)
        scenes_frame.rowconfigure(1, weight=1)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
    def setup_effects_tab(self):
        """Setup effects control tab"""
        effects_frame = ttk.Frame(self.notebook)
        self.notebook.add(effects_frame, text="Effects")
        
        # Effects selection
        select_frame = ttk.LabelFrame(effects_frame, text="Effects Selection", padding="10")
        select_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        ttk.Label(select_frame, text="Effect:").grid(row=0, column=0, sticky="w")
        self.fx_var = tk.IntVar(value=1)
        fx_spin = ttk.Spinbox(select_frame, from_=1, to=8, textvariable=self.fx_var, width=5)
        fx_spin.grid(row=0, column=1, padx=5)
        
        ttk.Label(select_frame, text="Type:").grid(row=0, column=2, sticky="w")
        self.fx_type_var = tk.StringVar(value="Hall Reverb")
        fx_type_combo = ttk.Combobox(select_frame, textvariable=self.fx_type_var, 
                                    values=["Hall Reverb", "Plate Reverb", "Room Reverb", "Delay", "Chorus"])
        fx_type_combo.grid(row=0, column=3, padx=5)
        
        ttk.Button(select_frame, text="Set Type", command=self.set_fx_type).grid(row=0, column=4, padx=5)
        
        # Effects parameters
        params_frame = ttk.LabelFrame(effects_frame, text="Parameters", padding="10")
        params_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        self.fx_params = {}
        param_names = ["Decay", "Pre Delay", "Size", "Density", "Diffusion"]
        
        for i, name in enumerate(param_names):
            ttk.Label(params_frame, text=f"{name}:").grid(row=i, column=0, sticky="w", padx=5, pady=2)
            
            param_var = tk.DoubleVar(value=0.5)
            param_scale = ttk.Scale(params_frame, from_=0.0, to=1.0, variable=param_var,
                                   orient="horizontal", length=200,
                                   command=lambda v, p=name: self.on_fx_param_change(p, float(v)))
            param_scale.grid(row=i, column=1, padx=5, pady=2)
            
            self.fx_params[name] = param_var
        
        # Configure grid weights
        effects_frame.columnconfigure(0, weight=1)
        effects_frame.rowconfigure(1, weight=1)
        params_frame.columnconfigure(1, weight=1)
        
    def toggle_connection(self):
        """Toggle connection to X32"""
        if not self.connection.connected:
            # Connect
            self.connection.ip_address = self.ip_var.get()
            self.connection.port = int(self.port_var.get())
            
            if self.connection.connect():
                self.status_var.set("Connected")
                self.connect_btn.config(text="Disconnect")
                messagebox.showinfo("Success", "Connected to X32!")
            else:
                messagebox.showerror("Error", "Failed to connect to X32")
        else:
            # Disconnect
            self.connection.disconnect()
            self.status_var.set("Disconnected")
            self.connect_btn.config(text="Connect")
    
    def on_ch_fader_change(self, channel: int, value: float):
        """Handle channel fader change"""
        if self.connection.connected:
            self.connection.set_channel_fader(channel, value)
    
    def on_ch_mute_change(self, channel: int, mute: bool):
        """Handle channel mute change"""
        if self.connection.connected:
            self.connection.set_channel_mute(channel, mute)
    
    def on_bus_fader_change(self, bus: int, value: float):
        """Handle bus fader change"""
        if self.connection.connected:
            self.connection.set_bus_fader(bus, value)
    
    def on_bus_mute_change(self, bus: int, mute: bool):
        """Handle bus mute change"""
        if self.connection.connected:
            self.connection.set_bus_mute(bus, mute)
    
    def on_main_fader_change(self, value: float):
        """Handle main fader change"""
        if self.connection.connected:
            self.connection.set_main_fader(value)
    
    def on_main_mute_change(self, mute: bool):
        """Handle main mute change"""
        if self.connection.connected:
            self.connection.set_main_mute(mute)
    
    def start_meters(self):
        """Start meter data streaming"""
        if self.connection.connected:
            self.connection.start_meters()
    
    def stop_meters(self):
        """Stop meter data streaming"""
        if self.connection.connected:
            self.connection.stop_meters()
    
    def load_scene_list(self):
        """Load list of scenes"""
        if self.connection.connected:
            self.connection.get_scene_list()
    
    def start_remote(self):
        """Start remote control mode"""
        if self.connection.connected:
            self.connection.start_remote()
    
    def stop_remote(self):
        """Stop remote control mode"""
        if self.connection.connected:
            self.connection.stop_remote()
    
    def load_selected_scene(self):
        """Load selected scene"""
        selection = self.scene_listbox.curselection()
        if selection and self.connection.connected:
            scene_num = selection[0] + 1
            self.connection.load_scene(scene_num)
    
    def save_scene_dialog(self):
        """Show save scene dialog"""
        name = tk.simpledialog.askstring("Save Scene", "Enter scene name:")
        if name and self.connection.connected:
            scene_num = 1  # Default scene number
            self.connection.save_scene(scene_num, name)
    
    def set_fx_type(self):
        """Set effects type"""
        if self.connection.connected:
            fx_num = self.fx_var.get()
            fx_type = self.fx_type_var.get()
            self.connection.set_fx_type(fx_num, fx_type)
    
    def on_fx_param_change(self, param: str, value: float):
        """Handle effects parameter change"""
        if self.connection.connected:
            fx_num = self.fx_var.get()
            self.connection.set_fx_param(fx_num, param, value)

def main():
    """Main application entry point"""
    root = tk.Tk()
    app = X32OSCApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 