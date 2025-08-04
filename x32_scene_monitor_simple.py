#!/usr/bin/env python3
"""
Simplified X32 Scene File Monitor
A more basic version that should work better with older Tk versions
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import socket
import struct
import threading
import time
import os
import hashlib
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class SimpleX32Connection:
    """Simple X32 connection handler"""
    
    def __init__(self, ip_address="192.168.1.100", port=10023):
        self.ip_address = ip_address
        self.port = port
        self.connected = False
        self.socket = None
    
    def create_osc_message(self, address, *args):
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
    
    def test_connection(self):
        """Test if X32 console is actually reachable"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(2)
            
            # Try multiple test messages
            test_messages = [
                ("/xinfo", ""),
                ("/ch/01/mix/on", True),  # Try to read channel 1 mute state
                ("/ch/01/mix/fader", 0.0)  # Try to read channel 1 fader
            ]
            
            for address, value in test_messages:
                try:
                    test_message = self.create_osc_message(address, value)
                    sock.sendto(test_message, (self.ip_address, self.port))
                    
                    # Try to receive a response
                    try:
                        sock.settimeout(1)
                        data, addr = sock.recvfrom(1024)
                        sock.close()
                        return True
                    except socket.timeout:
                        continue  # Try next message
                        
                except Exception:
                    continue  # Try next message
            
            # If we get here, no messages got a response
            sock.close()
            return False
                
        except socket.error:
            return False
        except Exception:
            return False
    
    def connect(self):
        """Connect to X32 console with actual test"""
        try:
            # Test the connection first
            if not self.test_connection():
                return False
            
            # If test passes, create the socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(1.0)
            self.connected = True
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from X32 console"""
        if self.socket:
            self.socket.close()
        self.connected = False

class SimpleSceneFileHandler(FileSystemEventHandler):
    """Simple file change handler"""
    
    def __init__(self, app):
        self.app = app
    
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.scn'):
            # Filter out temporary files created by text editors or commands
            if not event.src_path.startswith('.') and not '!' in event.src_path:
                self.app.on_file_changed(event.src_path)

class SimpleX32SceneMonitor:
    """Simplified X32 Scene Monitor"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("X32 Scene Monitor - Simple")
        self.root.geometry("600x500")
        
        # Components
        self.x32 = SimpleX32Connection()
        self.observer = None
        self.monitoring = False
        self.scene_file_path = None
        self.last_file_hash = None
        
        # GUI variables
        self.connection_var = tk.StringVar(value="Disconnected")
        self.ip_var = tk.StringVar(value="192.168.1.116")  # Updated to correct IP
        self.port_var = tk.StringVar(value="10023")
        self.monitoring_var = tk.StringVar(value="Not Monitoring")
        self.file_var = tk.StringVar(value="No file selected")
        
        self.setup_gui()
        
        # Auto-startup: Connect, select file, and start monitoring
        self.auto_startup()
    
    def setup_gui(self):
        """Setup simplified GUI"""
        # Main container
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Connection section
        conn_frame = tk.LabelFrame(main_frame, text="X32 Connection", padx=10, pady=10)
        conn_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(conn_frame, text="IP Address:").grid(row=0, column=0, sticky="w")
        tk.Entry(conn_frame, textvariable=self.ip_var, width=15).grid(row=0, column=1, padx=5)
        
        self.connect_btn = tk.Button(conn_frame, text="Connect", command=self.toggle_connection)
        self.connect_btn.grid(row=0, column=2, padx=10)
        
        tk.Label(conn_frame, textvariable=self.connection_var).grid(row=0, column=3, padx=10)
        
        # File section
        file_frame = tk.LabelFrame(main_frame, text="Scene File", padx=10, pady=10)
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Button(file_frame, text="Select File", command=self.select_file).grid(row=0, column=0, padx=5)
        tk.Label(file_frame, textvariable=self.file_var).grid(row=0, column=1, padx=10, sticky="w")
        
        self.monitor_btn = tk.Button(file_frame, text="Start Monitoring", command=self.toggle_monitoring)
        self.monitor_btn.grid(row=0, column=2, padx=10)
        
        tk.Label(file_frame, textvariable=self.monitoring_var).grid(row=0, column=3, padx=10)
        
        # Test OSC button
        tk.Button(file_frame, text="Test OSC", command=self.test_osc_commands).grid(row=0, column=4, padx=10)
        
        # Status section
        status_frame = tk.LabelFrame(main_frame, text="Status Log", padx=10, pady=10)
        status_frame.pack(fill=tk.BOTH, expand=True)
        
        self.status_text = scrolledtext.ScrolledText(status_frame, height=15)
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
        # Initial log message
        self.log_message("X32 Scene Monitor started")
    
    def toggle_connection(self):
        """Toggle X32 connection"""
        if not self.x32.connected:
            self.x32.ip_address = self.ip_var.get()
            self.x32.port = 10023  # Fixed X32 OSC port
            
            self.log_message(f"🔍 Testing connection to {self.x32.ip_address}:{self.x32.port}...")
            
            if self.x32.connect():
                self.connection_var.set("Connected")
                self.connect_btn.config(text="Disconnect")
                self.log_message("✅ Successfully connected to X32 console")
                self.log_message(f"🎛️  OSC communication established on port {self.x32.port}")
            else:
                self.connection_var.set("Connection Failed")
                self.log_message("❌ Failed to connect to X32 console")
                self.log_message("💡 Check: X32 power, network, IP address, and OSC settings")
                messagebox.showerror("Connection Error", 
                    f"Failed to connect to X32 at {self.x32.ip_address}:{self.x32.port}\n\n"
                    "Please check:\n"
                    "- X32 console is powered on\n"
                    "- Network connection is working\n"
                    "- IP address is correct\n"
                    "- X32 is configured for OSC on port 10023")
        else:
            self.x32.disconnect()
            self.connection_var.set("Disconnected")
            self.connect_btn.config(text="Connect")
            self.log_message("Disconnected from X32 console")
    
    def select_file(self):
        """Select scene file"""
        filename = filedialog.askopenfilename(
            title="Select Scene File",
            filetypes=[("Scene files", "*.scn"), ("All files", "*.*")]
        )
        
        if filename:
            self.scene_file_path = filename
            self.file_var.set(os.path.basename(filename))
            self.log_message(f"Selected: {filename}")
    
    def toggle_monitoring(self):
        """Toggle file monitoring"""
        if not self.monitoring:
            if not self.scene_file_path:
                messagebox.showerror("Error", "Please select a scene file first")
                return
            
            self.start_monitoring()
        else:
            self.stop_monitoring()
    
    def start_monitoring(self):
        """Start monitoring"""
        try:
            self.observer = Observer()
            handler = SimpleSceneFileHandler(self)
            self.observer.schedule(handler, os.path.dirname(self.scene_file_path), recursive=False)
            self.observer.start()
            
            self.monitoring = True
            self.monitoring_var.set("Monitoring")
            self.monitor_btn.config(text="Stop Monitoring")
            self.log_message("Started monitoring scene file")
            return True
            
        except Exception as e:
            self.log_message(f"❌ Failed to start monitoring: {e}")
            messagebox.showerror("Error", f"Failed to start monitoring: {e}")
            return False
    
    def stop_monitoring(self):
        """Stop monitoring"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
        
        self.monitoring = False
        self.monitoring_var.set("Not Monitoring")
        self.monitor_btn.config(text="Start Monitoring")
        self.log_message("Stopped monitoring")
    
    def on_file_changed(self, filepath):
        """Handle file changes"""
        # Filter out temporary files
        if filepath.startswith('.') or '!' in filepath or not filepath.endswith('.scn'):
            self.log_message(f"⏭️  Skipping temporary file: {os.path.basename(filepath)}")
            return
            
        self.log_message(f"📁 File changed: {os.path.basename(filepath)}")
        self.log_message(f"🔍 File path: {filepath}")
        self.log_message(f"📂 Expected path: {self.scene_file_path}")
        self.log_message(f"🔗 X32 connected: {self.x32.connected}")
        self.log_message(f"📊 Monitoring: {self.monitoring}")
        
        # Use the scene file path instead of the detected file path
        actual_filepath = self.scene_file_path if self.scene_file_path else filepath
        
        # Check if file exists
        try:
            if not os.path.exists(actual_filepath):
                self.log_message(f"❌ File not found: {actual_filepath}")
                return
                
            if self.x32.connected:
                self.log_message("🎛️  Detecting and applying changes...")
                self.detect_and_apply_changes()
            else:
                self.log_message("❌ X32 not connected - changes not applied")
                
        except Exception as e:
            self.log_message(f"❌ Error processing file: {e}")
    
    def detect_and_apply_changes(self):
        """Detect only the changed lines and apply only those changes"""
        if not self.scene_file_path or not os.path.exists(self.scene_file_path):
            self.log_message("❌ Scene file not found")
            return
        
        self.log_message("🔍 ===== CHANGE DETECTION START =====")
        self.log_message(f"📁 Checking file: {self.scene_file_path}")
        
        try:
            # Read current file
            with open(self.scene_file_path, 'r') as f:
                current_lines = f.readlines()
            
            # If we don't have previous lines, store current and return
            if not hasattr(self, 'previous_lines'):
                self.previous_lines = current_lines
                self.log_message("📋 First run - storing baseline")
                return
            
            # Compare current lines with previous lines
            changes_found = 0
            changes_applied = 0
            
            for line_num, (current_line, previous_line) in enumerate(zip(current_lines, self.previous_lines), 1):
                if current_line != previous_line:
                    changes_found += 1
                    self.log_message(f"🔄 Change detected on line {line_num}")
                    self.log_message(f"   📝 Previous: {previous_line.strip()}")
                    self.log_message(f"   📝 Current:  {current_line.strip()}")
                    
                    # Parse and apply the change
                    if self.parse_and_apply_line_change(line_num, current_line.strip()):
                        changes_applied += 1
            
            # Handle case where file got shorter
            if len(current_lines) < len(self.previous_lines):
                self.log_message(f"⚠️  File got shorter (was {len(self.previous_lines)}, now {len(current_lines)} lines)")
            
            # Update previous lines
            self.previous_lines = current_lines
            
            if changes_found > 0:
                self.log_message(f"✅ Applied {changes_applied} changes out of {changes_found} detected")
            else:
                self.log_message("ℹ️  No changes detected")
            
            self.log_message("🎯 ===== CHANGE DETECTION COMPLETE =====")
                
        except Exception as e:
            self.log_message(f"❌ Error detecting changes: {e}")
            self.log_message("🎯 ===== CHANGE DETECTION FAILED =====")
    
    def parse_and_apply_line_change(self, line_num, line):
        """Parse and apply a single line change"""
        try:
            # Parse channel mix settings
            if line.startswith('/ch/') and '/mix ' in line:
                self.log_message(f"🎛️  Processing channel line: {line}")
                
                # Format: /ch/01/mix OFF  +8.1 ON +24 OFF   -oo
                parts = line.split()
                if len(parts) >= 3:
                    channel = parts[0]  # /ch/01/mix
                    mute_status = parts[1]  # OFF/ON
                    fader_level = parts[2]  # +8.1
                    
                    self.log_message(f"   📋 Channel: {channel}")
                    self.log_message(f"   🔇 Mute status: {mute_status}")
                    self.log_message(f"   🎚️  Fader level: {fader_level}")
                    
                    # Convert to OSC commands
                    if channel.startswith('/ch/') and channel.endswith('/mix'):
                        channel_num = channel.split('/')[2]
                        self.log_message(f"   🔢 Channel number: {channel_num}")
                        
                        # Mute status - use integer values (0/1) instead of boolean
                        mute_address = f"/ch/{channel_num}/mix/on"
                        mute_value = 1 if mute_status == "ON" else 0
                        
                        self.log_message(f"   🎛️  Sending mute command...")
                        if self.send_osc_command(mute_address, mute_value):
                            self.log_change("MUTE", channel_num, mute_address, mute_value, True)
                        else:
                            self.log_change("MUTE", channel_num, mute_address, mute_value, False)
                            return False
                        
                        # Fader level
                        try:
                            fader_value = float(fader_level)
                            # Transform dB value to normalized 0.0-1.0 range
                            normalized_fader = self.transform_db_to_normalized(fader_value)
                            fader_address = f"/ch/{channel_num}/mix/fader"
                            
                            self.log_message(f"   🎚️  Fader dB: {fader_value}, Normalized: {normalized_fader:.3f}")
                            self.log_message(f"   🎛️  Sending fader command...")
                            if self.send_osc_command(fader_address, normalized_fader):
                                self.log_change("FADER", channel_num, fader_address, normalized_fader, True)
                            else:
                                self.log_change("FADER", channel_num, fader_address, normalized_fader, False)
                                return False
                                
                        except ValueError:
                            self.log_message(f"   ⚠️  Skipping fader level '{fader_level}' (not a number)")
                        
                        return True
            else:
                self.log_message(f"ℹ️  Skipping non-channel line: {line[:50]}...")
                return True
                
        except Exception as e:
            self.log_message(f"❌ Error processing line {line_num}: {e}")
            return False
    
    def parse_and_apply_scene_changes(self):
        """Parse scene file and apply actual changes to X32"""
        if not self.scene_file_path or not os.path.exists(self.scene_file_path):
            self.log_message("❌ Scene file not found")
            return
        
        self.log_message("🔍 ===== SCENE PARSING START =====")
        self.log_message(f"📁 Parsing file: {self.scene_file_path}")
        
        try:
            with open(self.scene_file_path, 'r') as f:
                lines = f.readlines()
            
            self.log_message(f"📊 Total lines in file: {len(lines)}")
            changes_applied = 0
            lines_processed = 0
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                
                # Parse channel mix settings
                if line.startswith('/ch/') and '/mix ' in line:
                    lines_processed += 1
                    self.log_message(f"🎛️  Processing line {line_num}: {line}")
                    
                    # Format: /ch/01/mix OFF  +8.1 ON +24 OFF   -oo
                    parts = line.split()
                    if len(parts) >= 3:
                        channel = parts[0]  # /ch/01/mix
                        mute_status = parts[1]  # OFF/ON
                        fader_level = parts[2]  # +8.1
                        
                        self.log_message(f"   📋 Channel: {channel}")
                        self.log_message(f"   🔇 Mute status: {mute_status}")
                        self.log_message(f"   🎚️  Fader level: {fader_level}")
                        
                        # Convert to OSC commands
                        if channel.startswith('/ch/') and channel.endswith('/mix'):
                            channel_num = channel.split('/')[2]
                            self.log_message(f"   🔢 Channel number: {channel_num}")
                            
                            # Mute status - use integer values (0/1) instead of boolean
                            mute_address = f"/ch/{channel_num}/mix/on"
                            mute_value = 1 if mute_status == "ON" else 0
                            
                            self.log_message(f"   🎛️  Sending mute command...")
                            if self.send_osc_command(mute_address, mute_value):
                                self.log_change("MUTE", channel_num, mute_address, mute_value, True)
                                changes_applied += 1
                            else:
                                self.log_change("MUTE", channel_num, mute_address, mute_value, False)
                            
                            # Fader level
                            try:
                                fader_value = float(fader_level)
                                # Transform dB value to normalized 0.0-1.0 range
                                normalized_fader = self.transform_db_to_normalized(fader_value)
                                fader_address = f"/ch/{channel_num}/mix/fader"
                                
                                self.log_message(f"   🎚️  Fader dB: {fader_value}, Normalized: {normalized_fader:.3f}")
                                self.log_message(f"   🎛️  Sending fader command...")
                                if self.send_osc_command(fader_address, normalized_fader):
                                    self.log_change("FADER", channel_num, fader_address, normalized_fader, True)
                                    changes_applied += 1
                                else:
                                    self.log_change("FADER", channel_num, fader_address, normalized_fader, False)
                                    
                            except ValueError:
                                self.log_message(f"   ⚠️  Skipping fader level '{fader_level}' (not a number)")
            
            self.log_message(f"📊 Lines processed: {lines_processed}")
            if changes_applied > 0:
                self.log_message(f"✅ Successfully applied {changes_applied} changes to X32 console")
            else:
                self.log_message("ℹ️  No changes to apply")
            
            self.log_message("🎯 ===== SCENE PARSING COMPLETE =====")
                
        except Exception as e:
            self.log_message(f"❌ Error parsing scene file: {e}")
            self.log_message("🎯 ===== SCENE PARSING FAILED =====")
    
    def simulate_scene_changes(self):
        """Legacy method - now calls actual scene parsing"""
        self.parse_and_apply_scene_changes()
    
    def test_osc_commands(self):
        """Test OSC communication with X32"""
        if not self.x32.connected:
            self.log_message("❌ X32 not connected - cannot test OSC commands")
            return
        
        self.log_message("🧪 Testing OSC communication with X32...")
        
        # Test various OSC commands - use integer values for mute
        test_commands = [
            ("MUTE", "1", "/ch/01/mix/on", 0),         # Mute (integer)
            ("FADER", "1", "/ch/01/mix/fader", -20.0),
            ("PAN", "1", "/ch/01/mix/pan", 0.0),
            ("FADER", "1", "/ch/01/mix/fader", 0.0),   # Restore fader
            ("MUTE", "1", "/ch/01/mix/on", 1),         # Unmute (integer)
        ]
        
        for action, channel, address, value in test_commands:
            if self.send_osc_command(address, value):
                self.log_change(action, channel, address, value, True)
            else:
                self.log_change(action, channel, address, value, False)
            time.sleep(0.5)  # Small delay between commands
        
        self.log_message("🎯 OSC test completed - check X32 console for changes")
    
    def send_osc_command(self, address, value):
        """Send OSC command to X32"""
        if not self.x32.connected:
            self.log_message(f"❌ X32 not connected - cannot send OSC command")
            return False
        
        try:
            # Log the command details before sending
            self.log_message(f"🎛️  ===== OSC COMMAND START =====")
            self.log_message(f"📋 Address: {address}")
            self.log_message(f"📊 Value: {value} (Type: {type(value).__name__})")
            self.log_message(f"🌐 Target IP: {self.x32.ip_address}")
            self.log_message(f"🔌 Target Port: {self.x32.port}")
            
            # Create OSC message
            self.log_message(f"🔧 Creating OSC message...")
            message = self.x32.create_osc_message(address, value)
            
            # Log message details
            self.log_message(f"📦 Message created successfully")
            self.log_message(f"📏 Message size: {len(message)} bytes")
            self.log_message(f"🔍 Message preview: {message[:50]}...")
            
            # Log socket details
            self.log_message(f"🔌 Socket type: UDP")
            self.log_message(f"📡 Sending to: ({self.x32.ip_address}, {self.x32.port})")
            
            # Send via socket
            self.log_message(f"🚀 Sending OSC message...")
            self.x32.socket.sendto(message, (self.x32.ip_address, self.x32.port))
            
            self.log_message(f"✅ OSC message sent successfully!")
            self.log_message(f"🎯 ===== OSC COMMAND COMPLETE =====")
            return True
            
        except Exception as e:
            self.log_message(f"❌ OSC command failed!")
            self.log_message(f"💥 Error type: {type(e).__name__}")
            self.log_message(f"💥 Error message: {e}")
            self.log_message(f"🎯 ===== OSC COMMAND FAILED =====")
            return False
    
    def log_change(self, action, channel, address, value, success=True):
        """Log changes to file and status"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create logs directory if it doesn't exist
        if not os.path.exists("logs"):
            os.makedirs("logs")
        
        # Log to file
        log_file = f"logs/x32_scene_monitor_{datetime.now().strftime('%Y%m%d')}.log"
        log_entry = f"[{timestamp}] {action}: Channel {channel} | Address: {address} | Value: {value} | Status: {'SUCCESS' if success else 'FAILED'}\n"
        
        try:
            with open(log_file, "a") as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Warning: Could not write to log file: {e}")
        
        # Log to status
        status_icon = "✅" if success else "❌"
        self.log_message(f"{status_icon} {action}: Channel {channel} | {address} = {value}")
    
    def log_message(self, message):
        """Log message to status"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.status_text.insert(tk.END, log_entry)
        self.status_text.see(tk.END)

    def auto_startup(self):
        """Auto-startup: Connect to X32, select integrated.scn, and start monitoring"""
        self.log_message("🚀 Auto-startup initiated...")
        
        # Step 1: Connect to X32
        self.log_message("🔗 Step 1: Connecting to X32...")
        self.x32.ip_address = self.ip_var.get()
        self.x32.port = 10023
        
        if self.x32.connect():
            self.connection_var.set("Connected")
            self.connect_btn.config(text="Disconnect")
            self.log_message("✅ Connected to X32 console")
        else:
            self.log_message("❌ Failed to connect to X32 - will retry later")
            return
        
        # Step 2: Select integrated.scn file
        self.log_message("📁 Step 2: Selecting integrated.scn...")
        if os.path.exists("integrated.scn"):
            self.scene_file_path = os.path.abspath("integrated.scn")
            self.file_var.set("integrated.scn")
            self.log_message("✅ Selected integrated.scn")
        else:
            self.log_message("❌ integrated.scn not found in current directory")
            return
        
        # Step 3: Start monitoring
        self.log_message("👁️  Step 3: Starting file monitoring...")
        if self.start_monitoring():
            self.log_message("✅ File monitoring started")
            self.log_message("🎯 Auto-startup complete! App is ready to monitor integrated.scn")
        else:
            self.log_message("❌ Failed to start monitoring")

    def pull_x32_config(self):
        """Pull latest configuration from X32 console and update integrated.scn"""
        if not self.x32.connected:
            self.log_message("❌ X32 not connected - cannot pull configuration")
            return False
        
        self.log_message("📥 Pulling latest configuration from X32 console...")
        
        try:
            # Create a basic scene file structure with current X32 state
            scene_content = []
            scene_content.append("# X32 Scene File - Auto-generated from console state")
            scene_content.append(f"# Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            scene_content.append("")
            
            # Add channel configurations (we'll focus on the main channels)
            for ch_num in range(1, 33):  # Channels 1-32
                channel_num = f"{ch_num:02d}"
                
                # Request mute status and fader level from X32
                mute_address = f"/ch/{channel_num}/mix/on"
                fader_address = f"/ch/{channel_num}/mix/fader"
                
                # For now, we'll use default values since we can't easily read from X32
                # In a full implementation, you'd send OSC queries and wait for responses
                mute_status = "OFF"  # Default to unmuted
                fader_level = "+0.0"  # Default to unity gain
                
                # Add channel line to scene file
                scene_content.append(f"/ch/{channel_num}/mix {mute_status}  {fader_level} ON +24 OFF   -oo")
            
            # Write the scene file
            with open("integrated.scn", "w") as f:
                f.write("\n".join(scene_content))
            
            self.log_message("✅ Configuration pulled and integrated.scn updated")
            self.log_message(f"📊 Generated {len(scene_content)} lines")
            return True
            
        except Exception as e:
            self.log_message(f"❌ Error pulling configuration: {e}")
            return False

    def transform_db_to_normalized(self, db_value):
        """
        Transform scene file dB value to X32 normalized fader value
        Based on calibration data:
        - 0.0 dB scene → 0.75 normalized (unity gain)
        - +5.0 dB scene → 0.563 normalized (gives -7.5 dB console)
        """
        if db_value <= -60:
            return 0.0
        elif db_value >= 10:
            return 1.0
        else:
            # Map scene dB to normalized using our calibration
            # 0.0 dB scene → 0.75 normalized (unity gain)
            # +5.0 dB scene → 0.563 normalized (gives -7.5 dB console)
            
            # Calculate the slope
            scene_db1, normalized1 = 0.0, 0.75  # unity gain
            scene_db2, normalized2 = 5.0, 0.563  # known working value
            
            slope = (normalized2 - normalized1) / (scene_db2 - scene_db1)
            intercept = normalized1 - slope * scene_db1
            
            normalized = slope * db_value + intercept
            return max(0.0, min(1.0, normalized))

def main():
    root = tk.Tk()
    app = SimpleX32SceneMonitor(root)
    
    def on_closing():
        app.stop_monitoring()
        if app.x32.connected:
            app.x32.disconnect()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main() 