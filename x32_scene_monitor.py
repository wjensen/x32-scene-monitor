#!/usr/bin/env python3
"""
X32 Scene File Monitor
Watches a local .scn file and automatically applies changes to X32 console
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import socket
import threading
import time
import json
import struct
import os
import hashlib
from typing import Dict, Any, Optional, List
import queue
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import re

class SceneParser:
    """Parse and apply X32 scene file changes"""
    
    def __init__(self):
        self.last_file_hash = None
        self.current_scene = {}
        self.changes_detected = []
        
    def calculate_file_hash(self, filepath: str) -> str:
        """Calculate MD5 hash of file to detect changes"""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            print(f"Error calculating file hash: {e}")
            return None
    
    def parse_scene_file(self, filepath: str) -> Dict[str, Any]:
        """Parse X32 scene file into structured data"""
        scene_data = {
            'channels': {},
            'buses': {},
            'main': {},
            'effects': {},
            'routing': {},
            'scenes': {}
        }
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Parse channel settings
                if line.startswith('/ch/'):
                    self._parse_channel_line(line, scene_data)
                
                # Parse bus settings
                elif line.startswith('/bus/'):
                    self._parse_bus_line(line, scene_data)
                
                # Parse main settings
                elif line.startswith('/main/'):
                    self._parse_main_line(line, scene_data)
                
                # Parse effects settings
                elif line.startswith('/fx/'):
                    self._parse_effect_line(line, scene_data)
                
                # Parse routing settings
                elif line.startswith('/config/routing'):
                    self._parse_routing_line(line, scene_data)
                
                # Parse scene settings
                elif line.startswith('/-ssn/'):
                    self._parse_scene_line(line, scene_data)
                    
        except Exception as e:
            print(f"Error parsing scene file: {e}")
            
        return scene_data
    
    def _parse_channel_line(self, line: str, scene_data: Dict):
        """Parse channel configuration line"""
        parts = line.split()
        if len(parts) < 2:
            return
            
        # Extract channel number
        match = re.search(r'/ch/(\d+)/', line)
        if not match:
            return
            
        ch_num = int(match.group(1))
        if ch_num not in scene_data['channels']:
            scene_data['channels'][ch_num] = {}
            
        # Parse different channel parameters
        if '/mix/fader' in line:
            try:
                fader_level = float(parts[1])
                scene_data['channels'][ch_num]['fader'] = fader_level
            except (ValueError, IndexError):
                pass
                
        elif '/mix/on' in line:
            try:
                mute_state = parts[1] == 'ON'
                scene_data['channels'][ch_num]['mute'] = mute_state
            except IndexError:
                pass
                
        elif '/mix/pan' in line:
            try:
                pan_value = float(parts[1])
                scene_data['channels'][ch_num]['pan'] = pan_value
            except (ValueError, IndexError):
                pass
                
        elif '/config/name' in line:
            try:
                name = parts[1].strip('"')
                scene_data['channels'][ch_num]['name'] = name
            except IndexError:
                pass
    
    def _parse_bus_line(self, line: str, scene_data: Dict):
        """Parse bus configuration line"""
        parts = line.split()
        if len(parts) < 2:
            return
            
        # Extract bus number
        match = re.search(r'/bus/(\d+)/', line)
        if not match:
            return
            
        bus_num = int(match.group(1))
        if bus_num not in scene_data['buses']:
            scene_data['buses'][bus_num] = {}
            
        # Parse different bus parameters
        if '/mix/fader' in line:
            try:
                fader_level = float(parts[1])
                scene_data['buses'][bus_num]['fader'] = fader_level
            except (ValueError, IndexError):
                pass
                
        elif '/mix/on' in line:
            try:
                mute_state = parts[1] == 'ON'
                scene_data['buses'][bus_num]['mute'] = mute_state
            except IndexError:
                pass
                
        elif '/config/name' in line:
            try:
                name = parts[1].strip('"')
                scene_data['buses'][bus_num]['name'] = name
            except IndexError:
                pass
    
    def _parse_main_line(self, line: str, scene_data: Dict):
        """Parse main configuration line"""
        parts = line.split()
        if len(parts) < 2:
            return
            
        if '/st/mix/fader' in line:
            try:
                fader_level = float(parts[1])
                scene_data['main']['fader'] = fader_level
            except (ValueError, IndexError):
                pass
                
        elif '/st/mix/on' in line:
            try:
                mute_state = parts[1] == 'ON'
                scene_data['main']['mute'] = mute_state
            except IndexError:
                pass
    
    def _parse_effect_line(self, line: str, scene_data: Dict):
        """Parse effects configuration line"""
        parts = line.split()
        if len(parts) < 2:
            return
            
        # Extract effect number
        match = re.search(r'/fx/(\d+)/', line)
        if not match:
            return
            
        fx_num = int(match.group(1))
        if fx_num not in scene_data['effects']:
            scene_data['effects'][fx_num] = {}
            
        if '/config/type' in line:
            try:
                fx_type = parts[1].strip('"')
                scene_data['effects'][fx_num]['type'] = fx_type
            except IndexError:
                pass
    
    def _parse_routing_line(self, line: str, scene_data: Dict):
        """Parse routing configuration line"""
        parts = line.split()
        if len(parts) < 2:
            return
            
        if '/config/routing/IN' in line:
            scene_data['routing']['inputs'] = parts[1:]
        elif '/config/routing/OUT' in line:
            scene_data['routing']['outputs'] = parts[1:]
    
    def _parse_scene_line(self, line: str, scene_data: Dict):
        """Parse scene configuration line"""
        parts = line.split()
        if len(parts) < 2:
            return
            
        # Extract scene number
        match = re.search(r'/-ssn/(\d+)/', line)
        if not match:
            return
            
        scene_num = int(match.group(1))
        if scene_num not in scene_data['scenes']:
            scene_data['scenes'][scene_num] = {}
            
        if '/config/name' in line:
            try:
                name = parts[1].strip('"')
                scene_data['scenes'][scene_num]['name'] = name
            except IndexError:
                pass
    
    def detect_changes(self, old_scene: Dict, new_scene: Dict) -> List[Dict]:
        """Detect changes between two scene states"""
        changes = []
        
        # Compare channels
        for ch_num in new_scene.get('channels', {}):
            old_ch = old_scene.get('channels', {}).get(ch_num, {})
            new_ch = new_scene['channels'][ch_num]
            
            for param in new_ch:
                if param not in old_ch or old_ch[param] != new_ch[param]:
                    changes.append({
                        'type': 'channel',
                        'number': ch_num,
                        'parameter': param,
                        'old_value': old_ch.get(param),
                        'new_value': new_ch[param]
                    })
        
        # Compare buses
        for bus_num in new_scene.get('buses', {}):
            old_bus = old_scene.get('buses', {}).get(bus_num, {})
            new_bus = new_scene['buses'][bus_num]
            
            for param in new_bus:
                if param not in old_bus or old_bus[param] != new_bus[param]:
                    changes.append({
                        'type': 'bus',
                        'number': bus_num,
                        'parameter': param,
                        'old_value': old_bus.get(param),
                        'new_value': new_bus[param]
                    })
        
        # Compare main
        old_main = old_scene.get('main', {})
        new_main = new_scene.get('main', {})
        
        for param in new_main:
            if param not in old_main or old_main[param] != new_main[param]:
                changes.append({
                    'type': 'main',
                    'parameter': param,
                    'old_value': old_main.get(param),
                    'new_value': new_main[param]
                })
        
        return changes

class X32Connection:
    """X32 console connection and control"""
    
    def __init__(self, ip_address: str = "192.168.1.100", port: int = 10023):
        self.ip_address = ip_address
        self.port = port
        self.socket = None
        self.connected = False
        
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
                pass
        
        return msg
    
    def apply_changes(self, changes: List[Dict]) -> bool:
        """Apply detected changes to X32 console"""
        if not self.connected:
            return False
        
        success_count = 0
        for change in changes:
            try:
                if change['type'] == 'channel':
                    success = self._apply_channel_change(change)
                elif change['type'] == 'bus':
                    success = self._apply_bus_change(change)
                elif change['type'] == 'main':
                    success = self._apply_main_change(change)
                else:
                    success = False
                
                if success:
                    success_count += 1
                    
            except Exception as e:
                print(f"Error applying change {change}: {e}")
        
        return success_count > 0
    
    def _apply_channel_change(self, change: Dict) -> bool:
        """Apply channel parameter change"""
        ch_num = change['number']
        param = change['parameter']
        value = change['new_value']
        
        if param == 'fader':
            return self.send_message(f"/ch/{ch_num:02d}/mix/fader", value)
        elif param == 'mute':
            return self.send_message(f"/ch/{ch_num:02d}/mix/on", 0 if value else 1)
        elif param == 'pan':
            return self.send_message(f"/ch/{ch_num:02d}/mix/pan", value)
        elif param == 'name':
            return self.send_message(f"/ch/{ch_num:02d}/config/name", value)
        
        return False
    
    def _apply_bus_change(self, change: Dict) -> bool:
        """Apply bus parameter change"""
        bus_num = change['number']
        param = change['parameter']
        value = change['new_value']
        
        if param == 'fader':
            return self.send_message(f"/bus/{bus_num:02d}/mix/fader", value)
        elif param == 'mute':
            return self.send_message(f"/bus/{bus_num:02d}/mix/on", 0 if value else 1)
        elif param == 'name':
            return self.send_message(f"/bus/{bus_num:02d}/config/name", value)
        
        return False
    
    def _apply_main_change(self, change: Dict) -> bool:
        """Apply main parameter change"""
        param = change['parameter']
        value = change['new_value']
        
        if param == 'fader':
            return self.send_message("/main/st/mix/fader", value)
        elif param == 'mute':
            return self.send_message("/main/st/mix/on", 0 if value else 1)
        
        return False

class SceneFileHandler(FileSystemEventHandler):
    """File system event handler for scene file changes"""
    
    def __init__(self, app):
        self.app = app
        self.last_modified = 0
        self.debounce_time = 1.0  # 1 second debounce
        
    def on_modified(self, event):
        """Handle file modification events"""
        if event.is_directory:
            return
            
        if not event.src_path.endswith('.scn'):
            return
            
        # Debounce rapid file changes
        current_time = time.time()
        if current_time - self.last_modified < self.debounce_time:
            return
            
        self.last_modified = current_time
        
        # Notify main application
        self.app.on_scene_file_changed(event.src_path)

class X32SceneMonitor:
    """Main application for monitoring scene files and applying changes"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("X32 Scene File Monitor")
        self.root.geometry("1000x700")
        
        # Components
        self.x32 = X32Connection()
        self.parser = SceneParser()
        self.observer = None
        self.monitoring = False
        
        # File monitoring
        self.scene_file_path = None
        self.last_scene_data = {}
        
        # GUI variables
        self.connection_var = tk.StringVar(value="Disconnected")
        self.ip_var = tk.StringVar(value="192.168.1.100")
        self.port_var = tk.IntVar(value=10023)
        self.monitoring_var = tk.StringVar(value="Not Monitoring")
        self.file_var = tk.StringVar(value="No file selected")
        
        self.setup_gui()
        
    def setup_gui(self):
        """Setup the GUI interface"""
        # Connection Frame
        conn_frame = ttk.LabelFrame(self.root, text="X32 Connection", padding="10")
        conn_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        ttk.Label(conn_frame, text="IP Address:").grid(row=0, column=0, sticky="w")
        ttk.Entry(conn_frame, textvariable=self.ip_var, width=15).grid(row=0, column=1, padx=5)
        
        ttk.Label(conn_frame, text="Port:").grid(row=0, column=2, sticky="w", padx=(10,0))
        ttk.Entry(conn_frame, textvariable=self.port_var, width=8).grid(row=0, column=3, padx=5)
        
        self.connect_btn = ttk.Button(conn_frame, text="Connect", command=self.toggle_connection)
        self.connect_btn.grid(row=0, column=4, padx=10)
        
        ttk.Label(conn_frame, textvariable=self.connection_var).grid(row=0, column=5, padx=10)
        
        # File Selection Frame
        file_frame = ttk.LabelFrame(self.root, text="Scene File", padding="10")
        file_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        ttk.Button(file_frame, text="Select Scene File", command=self.select_scene_file).grid(row=0, column=0, padx=5)
        ttk.Label(file_frame, textvariable=self.file_var).grid(row=0, column=1, padx=10, sticky="w")
        
        self.monitor_btn = ttk.Button(file_frame, text="Start Monitoring", command=self.toggle_monitoring)
        self.monitor_btn.grid(row=0, column=2, padx=10)
        
        ttk.Label(file_frame, textvariable=self.monitoring_var).grid(row=0, column=3, padx=10)
        
        # Status Frame
        status_frame = ttk.LabelFrame(self.root, text="Status", padding="10")
        status_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        self.status_text = scrolledtext.ScrolledText(status_frame, height=8, width=80)
        self.status_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Changes Frame
        changes_frame = ttk.LabelFrame(self.root, text="Recent Changes", padding="10")
        changes_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        self.changes_text = scrolledtext.ScrolledText(changes_frame, height=6, width=80)
        self.changes_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Configuration
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_rowconfigure(3, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
    def toggle_connection(self):
        """Toggle X32 connection"""
        if not self.x32.connected:
            # Connect
            self.x32.ip_address = self.ip_var.get()
            self.x32.port = self.port_var.get()
            
            if self.x32.connect():
                self.connection_var.set("Connected")
                self.connect_btn.config(text="Disconnect")
                self.log_message("Connected to X32 console")
            else:
                messagebox.showerror("Error", "Failed to connect to X32")
        else:
            # Disconnect
            self.x32.disconnect()
            self.connection_var.set("Disconnected")
            self.connect_btn.config(text="Connect")
            self.log_message("Disconnected from X32 console")
    
    def select_scene_file(self):
        """Select scene file to monitor"""
        filename = filedialog.askopenfilename(
            title="Select Scene File",
            filetypes=[("Scene files", "*.scn"), ("All files", "*.*")]
        )
        
        if filename:
            self.scene_file_path = filename
            self.file_var.set(os.path.basename(filename))
            self.log_message(f"Selected scene file: {filename}")
            
            # Parse initial scene
            self.last_scene_data = self.parser.parse_scene_file(filename)
            self.log_message("Initial scene parsed successfully")
    
    def toggle_monitoring(self):
        """Toggle file monitoring"""
        if not self.monitoring:
            if not self.scene_file_path:
                messagebox.showerror("Error", "Please select a scene file first")
                return
                
            if not self.x32.connected:
                messagebox.showerror("Error", "Please connect to X32 first")
                return
            
            # Start monitoring
            self.start_monitoring()
        else:
            # Stop monitoring
            self.stop_monitoring()
    
    def start_monitoring(self):
        """Start monitoring the scene file"""
        try:
            # Create observer
            self.observer = Observer()
            handler = SceneFileHandler(self)
            self.observer.schedule(handler, os.path.dirname(self.scene_file_path), recursive=False)
            self.observer.start()
            
            self.monitoring = True
            self.monitoring_var.set("Monitoring")
            self.monitor_btn.config(text="Stop Monitoring")
            self.log_message("Started monitoring scene file")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start monitoring: {e}")
    
    def stop_monitoring(self):
        """Stop monitoring the scene file"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
        
        self.monitoring = False
        self.monitoring_var.set("Not Monitoring")
        self.monitor_btn.config(text="Start Monitoring")
        self.log_message("Stopped monitoring scene file")
    
    def on_scene_file_changed(self, filepath: str):
        """Handle scene file change events"""
        self.log_message(f"Scene file changed: {os.path.basename(filepath)}")
        
        # Parse new scene
        new_scene_data = self.parser.parse_scene_file(filepath)
        
        # Detect changes
        changes = self.parser.detect_changes(self.last_scene_data, new_scene_data)
        
        if changes:
            self.log_message(f"Detected {len(changes)} changes")
            self.display_changes(changes)
            
            # Apply changes to X32
            if self.x32.connected:
                success = self.x32.apply_changes(changes)
                if success:
                    self.log_message("Changes applied to X32 console successfully")
                else:
                    self.log_message("Failed to apply some changes to X32 console")
            else:
                self.log_message("X32 not connected - changes not applied")
            
            # Update last scene data
            self.last_scene_data = new_scene_data
        else:
            self.log_message("No changes detected")
    
    def display_changes(self, changes: List[Dict]):
        """Display detected changes in the GUI"""
        self.changes_text.delete(1.0, tk.END)
        
        for change in changes:
            change_text = f"{change['type'].upper()}"
            if 'number' in change:
                change_text += f" {change['number']}"
            change_text += f" {change['parameter']}: {change['old_value']} → {change['new_value']}\n"
            self.changes_text.insert(tk.END, change_text)
    
    def log_message(self, message: str):
        """Log message to status text"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.status_text.insert(tk.END, log_entry)
        self.status_text.see(tk.END)
        
        # Limit log size
        lines = self.status_text.get(1.0, tk.END).split('\n')
        if len(lines) > 100:
            self.status_text.delete(1.0, f"{len(lines)-100}.0")

def main():
    root = tk.Tk()
    app = X32SceneMonitor(root)
    
    # Handle application shutdown
    def on_closing():
        app.stop_monitoring()
        if app.x32.connected:
            app.x32.disconnect()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main() 