#!/usr/bin/env python3
"""
Advanced X32 Remote Control Application
Enhanced version with scene management, EQ controls, and effects
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import socket
import threading
import time
import json
import struct
import os
from typing import Dict, Any, Optional, List
import queue

class X32AdvancedConnection:
    def __init__(self, ip_address: str = "192.168.1.100", port: int = 10023):
        self.ip_address = ip_address
        self.port = port
        self.socket = None
        self.connected = False
        self.message_queue = queue.Queue()
        self.response_queue = queue.Queue()
        self.listen_thread = None
        self.running = False
        
    def connect(self) -> bool:
        """Connect to X32 with bidirectional communication"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(1.0)
            self.socket.bind(('', 0))  # Bind to any available port
            self.connected = True
            self.running = True
            
            # Start listening thread
            self.listen_thread = threading.Thread(target=self._listen_for_responses)
            self.listen_thread.daemon = True
            self.listen_thread.start()
            
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from X32"""
        self.running = False
        if self.socket:
            self.socket.close()
        self.connected = False
    
    def _listen_for_responses(self):
        """Listen for responses from X32"""
        while self.running and self.connected:
            try:
                data, addr = self.socket.recvfrom(1024)
                self.response_queue.put(data)
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"Listen error: {e}")
    
    def send_message(self, address: str, *args):
        """Send OSC message to X32"""
        if not self.connected:
            return False
        
        try:
            msg = self._create_osc_message(address, *args)
            self.socket.sendto(msg, (self.ip_address, self.port))
            return True
        except Exception as e:
            print(f"Send failed: {e}")
            return False
    
    def _create_osc_message(self, address: str, *args) -> bytes:
        """Create proper OSC message"""
        # OSC address pattern
        msg = address.encode('utf-8')
        msg += b'\x00' * ((4 - len(msg) % 4) % 4)
        
        # Type tag string
        type_tags = ','
        for arg in args:
            if isinstance(arg, int):
                type_tags += 'i'
            elif isinstance(arg, float):
                type_tags += 'f'
            elif isinstance(arg, str):
                type_tags += 's'
            elif isinstance(arg, bool):
                type_tags += 'T' if arg else 'F'
        
        type_tags += '\x00'
        msg += type_tags.encode('utf-8')
        msg += b'\x00' * ((4 - len(type_tags) % 4) % 4)
        
        # Arguments
        for arg in args:
            if isinstance(arg, int):
                msg += struct.pack('>i', arg)
            elif isinstance(arg, float):
                msg += struct.pack('>f', arg)
            elif isinstance(arg, str):
                str_bytes = arg.encode('utf-8')
                msg += str_bytes
                msg += b'\x00' * ((4 - len(str_bytes) % 4) % 4)
            elif isinstance(arg, bool):
                # Boolean values don't add data to OSC message
                pass
        
        return msg
    
    # Channel Controls
    def send_channel_fader(self, channel: int, level: float):
        """Send channel fader level"""
        return self.send_message(f"/ch/{channel:02d}/mix/fader", level)
    
    def send_channel_mute(self, channel: int, mute: bool):
        """Send channel mute state"""
        return self.send_message(f"/ch/{channel:02d}/mix/on", 0 if mute else 1)
    
    def send_channel_pan(self, channel: int, pan: float):
        """Send channel pan position (-100 to +100)"""
        return self.send_message(f"/ch/{channel:02d}/mix/pan", pan)
    
    def send_channel_name(self, channel: int, name: str):
        """Send channel name"""
        return self.send_message(f"/ch/{channel:02d}/config/name", name)
    
    # EQ Controls
    def send_channel_eq_band(self, channel: int, band: int, enabled: bool, freq: float, gain: float, q: float):
        """Send channel EQ band settings"""
        base_addr = f"/ch/{channel:02d}/eq/{band}"
        self.send_message(f"{base_addr}/on", 1 if enabled else 0)
        self.send_message(f"{base_addr}/f", freq)
        self.send_message(f"{base_addr}/g", gain)
        self.send_message(f"{base_addr}/q", q)
    
    # Bus Controls
    def send_bus_fader(self, bus: int, level: float):
        """Send bus fader level"""
        return self.send_message(f"/bus/{bus:02d}/mix/fader", level)
    
    def send_bus_mute(self, bus: int, mute: bool):
        """Send bus mute state"""
        return self.send_message(f"/bus/{bus:02d}/mix/on", 0 if mute else 1)
    
    def send_bus_name(self, bus: int, name: str):
        """Send bus name"""
        return self.send_message(f"/bus/{bus:02d}/config/name", name)
    
    # Main Controls
    def send_main_fader(self, level: float):
        """Send main stereo fader level"""
        return self.send_message("/main/st/mix/fader", level)
    
    def send_main_mute(self, mute: bool):
        """Send main stereo mute state"""
        return self.send_message("/main/st/mix/on", 0 if mute else 1)
    
    # Effects Controls
    def send_fx_type(self, fx: int, fx_type: str):
        """Send effects type"""
        return self.send_message(f"/fx/{fx}/config/type", fx_type)
    
    def send_fx_param(self, fx: int, param: str, value: float):
        """Send effects parameter"""
        return self.send_message(f"/fx/{fx}/par/{param}", value)
    
    # Scene Management
    def load_scene(self, scene_number: int):
        """Load scene by number"""
        return self.send_message("/-action/goscene", scene_number)
    
    def save_scene(self, scene_number: int):
        """Save current scene to number"""
        return self.send_message("/-action/savescene", scene_number)
    
    def get_scene_name(self, scene_number: int):
        """Request scene name"""
        return self.send_message(f"/-ssn/{scene_number:03d}/config/name")

class X32AdvancedApp:
    def __init__(self, root):
        self.root = root
        self.root.title("X32 Advanced Remote Control")
        self.root.geometry("1400x900")
        
        # X32 Connection
        self.x32 = X32AdvancedConnection()
        
        # GUI Variables
        self.connection_var = tk.StringVar(value="Disconnected")
        self.ip_var = tk.StringVar(value="192.168.1.100")
        self.port_var = tk.IntVar(value=10023)
        
        # Scene management
        self.scenes = {}
        self.current_scene = 0
        
        self.setup_gui()
        self.setup_menu()
        
    def setup_menu(self):
        """Setup application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load Scene File", command=self.load_scene_file)
        file_menu.add_command(label="Save Scene File", command=self.save_scene_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Scene Manager", command=self.show_scene_manager)
        tools_menu.add_command(label="EQ Editor", command=self.show_eq_editor)
        tools_menu.add_command(label="Effects Rack", command=self.show_effects_rack)
        
    def setup_gui(self):
        """Setup the main GUI interface"""
        # Connection Frame
        conn_frame = ttk.LabelFrame(self.root, text="Connection", padding="10")
        conn_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
        
        ttk.Label(conn_frame, text="IP Address:").grid(row=0, column=0, sticky="w")
        ttk.Entry(conn_frame, textvariable=self.ip_var, width=15).grid(row=0, column=1, padx=5)
        
        ttk.Label(conn_frame, text="Port:").grid(row=0, column=2, sticky="w", padx=(10,0))
        ttk.Entry(conn_frame, textvariable=self.port_var, width=8).grid(row=0, column=3, padx=5)
        
        self.connect_btn = ttk.Button(conn_frame, text="Connect", command=self.toggle_connection)
        self.connect_btn.grid(row=0, column=4, padx=10)
        
        ttk.Label(conn_frame, textvariable=self.connection_var).grid(row=0, column=5, padx=10)
        
        # Scene Info
        ttk.Label(conn_frame, text="Scene:").grid(row=0, column=6, sticky="w", padx=(20,0))
        self.scene_var = tk.StringVar(value="None")
        ttk.Label(conn_frame, textvariable=self.scene_var).grid(row=0, column=7, padx=5)
        
        # Main Control Frame
        main_frame = ttk.Frame(self.root)
        main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=0, column=0, sticky="nsew")
        
        # Setup tabs
        self.setup_faders_tab()
        self.setup_eq_tab()
        self.setup_effects_tab()
        self.setup_scenes_tab()
        
        # Configuration
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
    def setup_faders_tab(self):
        """Setup faders control tab"""
        faders_frame = ttk.Frame(self.notebook)
        self.notebook.add(faders_frame, text="Faders")
        
        # Channel Faders
        ch_frame = ttk.LabelFrame(faders_frame, text="Channel Faders", padding="10")
        ch_frame.grid(row=0, column=0, sticky="nsew", padx=(0,5))
        
        self.ch_faders = {}
        self.ch_mutes = {}
        self.ch_pans = {}
        self.ch_names = {}
        
        # Create channel controls
        for i in range(16):  # 16 channels
            ch_num = i + 1
            row = i // 4
            col = i % 4
            
            # Channel frame
            ch_control_frame = ttk.Frame(ch_frame)
            ch_control_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            
            # Channel name
            name_var = tk.StringVar(value=f"Ch{ch_num}")
            self.ch_names[ch_num] = name_var
            ttk.Entry(ch_control_frame, textvariable=name_var, width=8).grid(row=0, column=0, columnspan=2, pady=2)
            
            # Fader
            fader_var = tk.DoubleVar(value=0.0)
            self.ch_faders[ch_num] = fader_var
            fader = ttk.Scale(ch_control_frame, from_=-60, to=10, variable=fader_var,
                            orient="vertical", length=120,
                            command=lambda val, ch=ch_num: self.on_channel_fader_change(ch, float(val)))
            fader.grid(row=1, column=0, pady=2)
            
            # Fader value
            fader_label = ttk.Label(ch_control_frame, text="0.0")
            fader_label.grid(row=1, column=1, padx=2)
            
            # Pan
            pan_var = tk.DoubleVar(value=0.0)
            self.ch_pans[ch_num] = pan_var
            pan = ttk.Scale(ch_control_frame, from_=-100, to=100, variable=pan_var,
                           orient="horizontal", length=80,
                           command=lambda val, ch=ch_num: self.on_channel_pan_change(ch, float(val)))
            pan.grid(row=2, column=0, columnspan=2, pady=2)
            
            # Mute button
            mute_var = tk.BooleanVar()
            self.ch_mutes[ch_num] = mute_var
            mute_btn = ttk.Checkbutton(ch_control_frame, text="M", variable=mute_var,
                                     command=lambda ch=ch_num: self.on_channel_mute_change(ch))
            mute_btn.grid(row=3, column=0, columnspan=2, pady=2)
        
        # Bus Faders
        bus_frame = ttk.LabelFrame(faders_frame, text="Bus Faders", padding="10")
        bus_frame.grid(row=0, column=1, sticky="nsew", padx=(5,0))
        
        self.bus_faders = {}
        self.bus_mutes = {}
        self.bus_names = {}
        
        # Create bus controls
        for i in range(8):  # 8 buses
            bus_num = i + 1
            
            # Bus frame
            bus_control_frame = ttk.Frame(bus_frame)
            bus_control_frame.grid(row=i, column=0, padx=5, pady=5, sticky="nsew")
            
            # Bus name
            name_var = tk.StringVar(value=f"Bus{bus_num}")
            self.bus_names[bus_num] = name_var
            ttk.Entry(bus_control_frame, textvariable=name_var, width=8).grid(row=0, column=0, columnspan=2, pady=2)
            
            # Fader
            fader_var = tk.DoubleVar(value=0.0)
            self.bus_faders[bus_num] = fader_var
            fader = ttk.Scale(bus_control_frame, from_=-60, to=10, variable=fader_var,
                            orient="vertical", length=120,
                            command=lambda val, bus=bus_num: self.on_bus_fader_change(bus, float(val)))
            fader.grid(row=1, column=0, pady=2)
            
            # Fader value
            fader_label = ttk.Label(bus_control_frame, text="0.0")
            fader_label.grid(row=1, column=1, padx=2)
            
            # Mute button
            mute_var = tk.BooleanVar()
            self.bus_mutes[bus_num] = mute_var
            mute_btn = ttk.Checkbutton(bus_control_frame, text="M", variable=mute_var,
                                     command=lambda bus=bus_num: self.on_bus_mute_change(bus))
            mute_btn.grid(row=2, column=0, columnspan=2, pady=2)
        
        # Main Fader
        main_frame = ttk.LabelFrame(faders_frame, text="Main Stereo", padding="10")
        main_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10,0))
        
        self.main_fader_var = tk.DoubleVar(value=0.0)
        main_fader = ttk.Scale(main_frame, from_=-60, to=10, variable=self.main_fader_var,
                              orient="horizontal", length=400,
                              command=lambda val: self.on_main_fader_change(float(val)))
        main_fader.grid(row=0, column=0, padx=10, pady=5)
        
        self.main_fader_label = ttk.Label(main_frame, text="0.0 dB")
        self.main_fader_label.grid(row=0, column=1, padx=10, pady=5)
        
        self.main_mute_var = tk.BooleanVar()
        main_mute_btn = ttk.Checkbutton(main_frame, text="Main Mute", variable=self.main_mute_var,
                                       command=self.on_main_mute_change)
        main_mute_btn.grid(row=0, column=2, padx=10, pady=5)
        
        # Configure grid weights
        faders_frame.grid_columnconfigure(0, weight=1)
        faders_frame.grid_columnconfigure(1, weight=1)
        faders_frame.grid_rowconfigure(0, weight=1)
        
    def setup_eq_tab(self):
        """Setup EQ control tab"""
        eq_frame = ttk.Frame(self.notebook)
        self.notebook.add(eq_frame, text="EQ")
        
        # EQ controls will be implemented here
        ttk.Label(eq_frame, text="EQ Editor - Coming Soon").pack(pady=50)
        
    def setup_effects_tab(self):
        """Setup effects control tab"""
        fx_frame = ttk.Frame(self.notebook)
        self.notebook.add(fx_frame, text="Effects")
        
        # Effects controls will be implemented here
        ttk.Label(fx_frame, text="Effects Rack - Coming Soon").pack(pady=50)
        
    def setup_scenes_tab(self):
        """Setup scene management tab"""
        scenes_frame = ttk.Frame(self.notebook)
        self.notebook.add(scenes_frame, text="Scenes")
        
        # Scene list
        list_frame = ttk.Frame(scenes_frame)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ttk.Label(list_frame, text="Scene List:").pack(anchor="w")
        
        # Scene listbox
        self.scene_listbox = tk.Listbox(list_frame, height=15)
        self.scene_listbox.pack(fill="both", expand=True, pady=5)
        
        # Scene buttons
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(fill="x", pady=5)
        
        ttk.Button(btn_frame, text="Load Scene", command=self.load_selected_scene).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Save Scene", command=self.save_current_scene).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Refresh", command=self.refresh_scenes).pack(side="left", padx=5)
        
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
                self.refresh_scenes()
            else:
                messagebox.showerror("Error", "Failed to connect to X32")
        else:
            # Disconnect
            self.x32.disconnect()
            self.connection_var.set("Disconnected")
            self.connect_btn.config(text="Connect")
            messagebox.showinfo("Info", "Disconnected from X32")
    
    # Event handlers
    def on_channel_fader_change(self, channel: int, value: float):
        """Handle channel fader change"""
        if self.x32.connected:
            self.x32.send_channel_fader(channel, value)
    
    def on_channel_pan_change(self, channel: int, value: float):
        """Handle channel pan change"""
        if self.x32.connected:
            self.x32.send_channel_pan(channel, value)
    
    def on_channel_mute_change(self, channel: int):
        """Handle channel mute change"""
        if self.x32.connected:
            mute = self.ch_mutes[channel].get()
            self.x32.send_channel_mute(channel, mute)
    
    def on_bus_fader_change(self, bus: int, value: float):
        """Handle bus fader change"""
        if self.x32.connected:
            self.x32.send_bus_fader(bus, value)
    
    def on_bus_mute_change(self, bus: int):
        """Handle bus mute change"""
        if self.x32.connected:
            mute = self.bus_mutes[bus].get()
            self.x32.send_bus_mute(bus, mute)
    
    def on_main_fader_change(self, value: float):
        """Handle main fader change"""
        if self.x32.connected:
            self.x32.send_main_fader(value)
            self.main_fader_label.config(text=f"{value:.1f} dB")
    
    def on_main_mute_change(self):
        """Handle main mute change"""
        if self.x32.connected:
            mute = self.main_mute_var.get()
            self.x32.send_main_mute(mute)
    
    # Scene management
    def load_scene_file(self):
        """Load scene file from disk"""
        filename = filedialog.askopenfilename(
            title="Load Scene File",
            filetypes=[("Scene files", "*.scn"), ("All files", "*.*")]
        )
        if filename:
            # Implementation for loading scene file
            messagebox.showinfo("Info", f"Loading scene file: {filename}")
    
    def save_scene_file(self):
        """Save current scene to disk"""
        filename = filedialog.asksaveasfilename(
            title="Save Scene File",
            defaultextension=".scn",
            filetypes=[("Scene files", "*.scn"), ("All files", "*.*")]
        )
        if filename:
            # Implementation for saving scene file
            messagebox.showinfo("Info", f"Saving scene file: {filename}")
    
    def show_scene_manager(self):
        """Show scene manager dialog"""
        # Implementation for scene manager
        messagebox.showinfo("Info", "Scene Manager - Coming Soon")
    
    def show_eq_editor(self):
        """Show EQ editor dialog"""
        # Implementation for EQ editor
        messagebox.showinfo("Info", "EQ Editor - Coming Soon")
    
    def show_effects_rack(self):
        """Show effects rack dialog"""
        # Implementation for effects rack
        messagebox.showinfo("Info", "Effects Rack - Coming Soon")
    
    def refresh_scenes(self):
        """Refresh scene list"""
        if not self.x32.connected:
            return
        
        # Clear current list
        self.scene_listbox.delete(0, tk.END)
        
        # Request scene names (this would need proper OSC implementation)
        for i in range(100):  # First 100 scenes
            self.x32.get_scene_name(i)
            self.scene_listbox.insert(tk.END, f"Scene {i:03d}")
    
    def load_selected_scene(self):
        """Load selected scene"""
        selection = self.scene_listbox.curselection()
        if selection:
            scene_num = selection[0]
            if self.x32.connected:
                self.x32.load_scene(scene_num)
                self.current_scene = scene_num
                self.scene_var.set(f"Scene {scene_num:03d}")
                messagebox.showinfo("Success", f"Loaded Scene {scene_num:03d}")
    
    def save_current_scene(self):
        """Save current scene"""
        if self.x32.connected:
            self.x32.save_scene(self.current_scene)
            messagebox.showinfo("Success", f"Saved Scene {self.current_scene:03d}")

def main():
    root = tk.Tk()
    app = X32AdvancedApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 