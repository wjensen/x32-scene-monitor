# X32 Scene File Monitor

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/x32-scene-monitor.svg)](https://badge.fury.io/py/x32-scene-monitor)

A Python application that watches X32 scene files (`.scn`) and automatically applies changes to the Behringer X32 digital mixing console in real-time. Perfect for seamless integration between scene file editing and live console control.

## 🎯 **What It Does**

The X32 Scene File Monitor creates a bridge between scene file editing and real-time console control:

1. **Watches your `.scn` file** for any changes
2. **Detects specific parameter modifications** (faders, mutes, names, etc.)
3. **Sends OSC commands** directly to your X32 console
4. **Applies changes immediately** without manual intervention

## 🚀 **Quick Start**

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/x32-scene-monitor.git
cd x32-scene-monitor

# Install dependencies
pip install -r requirements.txt

# Run the application
python x32_scene_monitor.py
```

### Basic Usage
1. **Connect to X32** (enter IP address)
2. **Select your scene file** (e.g., `X32_Rack.scn`)
3. **Start monitoring** for automatic updates
4. **Edit scene file** → Changes apply to console automatically!

## 🎛️ **Perfect Workflow**

### **AI-Assisted Editing (Recommended)**
```
You: "Set Aaron's channel to -8dB and mute his monitor"
AI: Edits scene file with precise changes
Monitor: Detects changes and applies to X32
Console: Immediately updates Aaron's levels
```

### **Manual Scene Editing**
```
Edit scene file → Monitor detects changes → Console updates automatically
```

## ✨ **Key Features**

- **📁 Real-time File Monitoring** - Watches `.scn` files for instant change detection
- **🎛️ Direct X32 Control** - OSC protocol communication with immediate parameter application
- **🔍 Intelligent Change Detection** - Parses and compares scene states to identify specific changes
- **🖥️ User-Friendly GUI** - Tkinter interface with connection management and status monitoring
- **🛡️ Safety & Reliability** - Error handling, validation, and debounced updates
- **📊 Detailed Logging** - Real-time status updates and change history
- **🔧 Cross-Platform** - Works on Windows, macOS, and Linux

## 🎛️ **Applications**

### **X32 Scene File Monitor** (`x32_scene_monitor.py`)
The main application that monitors local `.scn` files and automatically applies changes to the X32 console in real-time.

### **X32 OSC Protocol** (`x32_osc_protocol.py`)
Complete OSC protocol implementation based on official X32-OSC.pdf specifications. Provides comprehensive control over all X32 parameters with proper OSC message formatting and bidirectional communication.

### **X32 Advanced Remote Control** (`x32_advanced_remote.py`)
Enhanced remote control application with tabbed interface, scene management, and effects control.

### **X32 Remote Control** (`x32_remote_control.py`)
Basic remote control application for fader and mute control.

## 📋 **Supported X32 Parameters**

| Parameter Type | OSC Address | Description |
|----------------|-------------|-------------|
| **Channel Faders** | `/ch/XX/mix/fader` | -60dB to +10dB |
| **Channel Mutes** | `/ch/XX/mix/on` | ON/OFF states |
| **Channel Names** | `/ch/XX/config/name` | Text changes |
| **Channel Pan** | `/ch/XX/mix/pan` | -100 to +100 |
| **Bus Faders** | `/bus/XX/mix/fader` | -60dB to +10dB |
| **Bus Mutes** | `/bus/XX/mix/on` | ON/OFF states |
| **Main Fader** | `/main/st/mix/fader` | -60dB to +10dB |
| **Main Mute** | `/main/st/mix/on` | ON/OFF state |
| **Effects Types** | `/fx/XX/config/type` | Effect selection |
| **Routing** | `/config/routing/IN` | Input/output routing |

## 🛠️ **Installation & Setup**

### Prerequisites
- **Python 3.7 or higher**
- **Network connection** to X32 (WiFi or Ethernet)
- **X32 console** with OSC enabled

### Dependencies
```bash
# Core dependencies (included with Python)
tkinter      # GUI framework
socket       # Network communication
threading    # Multi-threading support
struct       # Binary data handling
queue        # Thread-safe queues

# Required external dependency
watchdog>=2.1.0  # File system monitoring
```

## 📖 **Usage Examples**

### Example 1: AI-Assisted Mixing
```python
# You ask AI to adjust Aaron's levels
# AI edits scene file:
/ch/02/mix ON  -8.0 ON +8 OFF   -oo  # Aaron's fader to -8dB
/bus/03/mix ON -oo OFF -100 OFF   -oo  # Mute Aaron's monitor L
/bus/04/mix ON -oo OFF +100 OFF   -oo  # Mute Aaron's monitor R

# Monitor detects changes and sends to X32:
# CHANNEL 2 fader: 2.0 → -8.0
# BUS 3 fader: -10.0 → -oo (muted)
# BUS 4 fader: -10.0 → -oo (muted)
```

### Example 2: Manual Scene Editing
```bash
# Edit scene file in any text editor
# Monitor automatically detects and applies changes
# No manual console interaction needed
```

## 🔧 **X32 Console Setup**

### 1. Enable OSC on X32
1. **Navigate to Setup** → `Global` → `Remote`
2. **Set Remote Protocol** to `OSC`
3. **Note IP address** and port (default: 10023)
4. **Ensure network connectivity** between X32 and computer

### 2. Application Configuration
1. **Launch X32 Scene Monitor**
2. **Enter X32 IP address** (e.g., 192.168.1.100)
3. **Click "Connect"** to establish connection
4. **Select scene file** to monitor
5. **Start monitoring** for automatic updates

## 🎯 **Use Cases**

### **Live Sound Engineering**
- **Real-time adjustments** during performances
- **Quick parameter changes** without console access
- **Remote mixing** from different locations
- **Backup console configurations**

### **Studio Recording**
- **Session management** with scene files
- **Automated parameter recall**
- **Multi-session consistency**
- **Client preference storage**

### **System Integration**
- **Automated venue setups**
- **Scheduled configuration changes**
- **Multi-console synchronization**
- **Backup and restore operations**

## 🔍 **Troubleshooting**

### **Connection Issues**
1. **Check IP address** - Ensure correct X32 IP
2. **Network connectivity** - Verify same network
3. **OSC enabled** - Confirm OSC is enabled on X32
4. **Firewall** - Check for blocking UDP port 10023

### **Control Issues**
1. **Permission errors** - Some parameters may be locked
2. **Range errors** - Ensure values are within valid ranges
3. **Response delays** - Normal for network communication

### **Performance Issues**
1. **Network latency** - Use wired connection if possible
2. **Multiple clients** - Limit concurrent connections
3. **Update frequency** - Reduce update rate if needed

## 📚 **Documentation**

- **[Feature Documentation](X32_Scene_Monitor_Features.md)** - Detailed feature overview
- **[Scene File Format](scn_file_documentation.txt)** - X32 scene file structure
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute to the project
- **[Changelog](CHANGELOG.md)** - Version history and changes

## 🤝 **Contributing**

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### **Ways to Contribute**
- 🐛 **Report bugs** via [GitHub Issues](https://github.com/yourusername/x32-scene-monitor/issues)
- 💡 **Suggest features** for future releases
- 🔧 **Submit code** improvements and fixes
- 📖 **Improve documentation** and examples
- 🧪 **Test** with different X32 configurations

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **Behringer** for the X32 platform and OSC protocol
- **Python Community** for excellent libraries and tools
- **Open Source Contributors** for inspiration and guidance
- **X32 User Community** for feedback and testing

## 🔗 **Links**

- **Repository**: [GitHub](https://github.com/yourusername/x32-scene-monitor)
- **Issues**: [Bug Reports & Feature Requests](https://github.com/yourusername/x32-scene-monitor/issues)
- **Discussions**: [Community Forum](https://github.com/yourusername/x32-scene-monitor/discussions)
- **X32 Documentation**: [Behringer X32](https://behringer.com/x32/docs)

---

**⭐ Star this repository if you find it useful!**

 