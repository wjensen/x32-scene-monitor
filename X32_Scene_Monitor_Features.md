# X32 Scene File Monitor Features

## 🎯 **Core Purpose**
The X32 Scene File Monitor is a Python application that watches a local `.scn` file and automatically applies changes to the X32 console when modifications are detected. This enables seamless integration between scene file editing and real-time console control.

## 📁 **File Monitoring**

### **Real-time File Watching**
- **Watches your `.scn` file** for any changes
- **Instant detection** of file modifications
- **Cross-platform compatibility** (Windows, macOS, Linux)
- **Debounced updates** to prevent rapid-fire changes (1-second debounce)

### **Intelligent Change Detection**
- **MD5 hash comparison** for reliable change detection
- **Parses scene file structure** into organized data
- **Compares before/after states** to identify specific changes
- **Filters relevant parameters** (ignores comments, empty lines)

## 🎛️ **Direct Console Control**

### **X32 Connection**
- **WiFi/Ethernet connection** to X32 console
- **OSC protocol communication** (Open Sound Control)
- **Configurable IP address** and port (default: 192.168.1.100:10023)
- **Connection status monitoring** with real-time feedback

### **Automatic Parameter Application**
- **Sends OSC commands** directly to console
- **Real-time parameter updates** without manual intervention
- **Error handling** for network issues
- **Success/failure logging** for each change

## 📊 **Change Detection & Parsing**

### **Supported Parameter Types**
- **Channel faders** (-60dB to +10dB)
- **Channel mutes** (ON/OFF states)
- **Channel names** (text changes)
- **Channel pan** (-100 to +100)
- **Bus faders** and mutes
- **Main stereo fader** and mute
- **Effects parameters** and types
- **Routing configurations**
- **Scene names** and metadata

### **Change Analysis**
- **Detailed change logging** with timestamps
- **Before/after value comparison**
- **Parameter type identification**
- **Change categorization** (channel, bus, main, effects)

## 🖥️ **User Interface**

### **Connection Management**
- **IP address configuration**
- **Port number settings**
- **Connect/disconnect controls**
- **Connection status indicators**

### **File Management**
- **Scene file selection** via file dialog
- **File path display**
- **Monitoring start/stop controls**
- **File change status indicators**

### **Status Monitoring**
- **Real-time status log** with timestamps
- **Change detection notifications**
- **Error reporting** and troubleshooting info
- **Application state indicators**

### **Change Display**
- **Recent changes list** with details
- **Parameter change history**
- **Before/after value display**
- **Change type categorization**

## 🔧 **Technical Features**

### **Scene File Parsing**
- **ASCII text parsing** of `.scn` files
- **Regular expression matching** for parameter extraction
- **Structured data organization** by parameter type
- **Error handling** for malformed files

### **OSC Protocol Implementation**
- **Proper OSC message formatting**
- **Type tag generation** (int, float, string, boolean)
- **Message encoding** and transmission
- **UDP socket management**

### **File System Monitoring**
- **Watchdog library integration**
- **Directory monitoring** for file changes
- **Event-driven architecture**
- **Cross-platform file system events**

## 🚀 **Usage Workflows**

### **Option 1: AI-Assisted Editing (Recommended)**
1. **AI edits scene file** based on user prompts
2. **Scene monitor detects** file modifications
3. **Changes apply automatically** to X32 console
4. **Real-time feedback** in monitor interface
5. **Immediate console response** to AI modifications

### **Option 2: Manual Scene Editing**
1. **User edits scene file** manually or with external tools
2. **Scene monitor detects** changes automatically
3. **Console updates** without manual intervention
4. **Change log** shows exactly what was modified
5. **Verification** of applied changes

### **Option 3: Batch Processing**
1. **Multiple changes** made to scene file
2. **All changes detected** and parsed
3. **Bulk application** to console
4. **Comprehensive change log** for review
5. **Error reporting** for failed changes

## 🛡️ **Safety & Reliability**

### **Error Handling**
- **Network connection failures**
- **File parsing errors**
- **OSC message transmission failures**
- **Invalid parameter values**
- **File system access issues**

### **Data Protection**
- **Change validation** before application
- **Parameter range checking**
- **Type safety** for all values
- **Rollback capability** through scene file

### **Performance Optimization**
- **Debounced file changes** (prevents rapid updates)
- **Efficient parsing** of large scene files
- **Memory management** for long-running sessions
- **Background processing** for file monitoring

## 📋 **Supported X32 Parameters**

### **Channel Controls**
- `/ch/XX/mix/fader` - Channel fader levels
- `/ch/XX/mix/on` - Channel mute states
- `/ch/XX/mix/pan` - Channel pan positions
- `/ch/XX/config/name` - Channel names

### **Bus Controls**
- `/bus/XX/mix/fader` - Bus fader levels
- `/bus/XX/mix/on` - Bus mute states
- `/bus/XX/config/name` - Bus names

### **Main Controls**
- `/main/st/mix/fader` - Main stereo fader
- `/main/st/mix/on` - Main stereo mute

### **Effects Controls**
- `/fx/XX/config/type` - Effects types
- `/fx/XX/par/XX` - Effects parameters

### **Routing Controls**
- `/config/routing/IN` - Input routing
- `/config/routing/OUT` - Output routing

## 🔄 **Integration Capabilities**

### **External Tools**
- **X32-Edit compatibility** (edit in X32-Edit, monitor applies changes)
- **Text editor integration** (edit in any text editor)
- **Version control systems** (Git, SVN)
- **Backup systems** (automatic scene file backups)

### **Automation**
- **Script integration** (Python, batch, shell scripts)
- **Scheduled updates** (cron jobs, task scheduler)
- **API integration** (REST APIs, webhooks)
- **Database integration** (scene parameter storage)

## 📈 **Monitoring & Logging**

### **Activity Logging**
- **Timestamped events** for all activities
- **Change detection logs** with details
- **Error logging** with stack traces
- **Performance metrics** (response times, success rates)

### **Status Reporting**
- **Connection status** (connected/disconnected)
- **File monitoring status** (active/inactive)
- **Change application status** (success/failure)
- **System resource usage** (memory, CPU)

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

## 🔮 **Future Enhancements**

### **Planned Features**
- **EQ parameter monitoring** and application
- **Dynamics processing** parameter changes
- **Effects rack** full parameter control
- **MIDI integration** for external control surfaces

### **Advanced Capabilities**
- **Multi-file monitoring** (multiple scene files)
- **Change scheduling** (delayed application)
- **Conditional changes** (if/then logic)
- **Change validation** (parameter range checking)

### **User Experience**
- **Web interface** for remote access
- **Mobile app** for iOS/Android
- **Voice control** integration
- **Gesture control** support

---

## 📝 **Installation & Setup**

### **Requirements**
- Python 3.7 or higher
- `watchdog` library for file monitoring
- Network connection to X32 console
- X32 console with OSC enabled

### **Quick Start**
```bash
# Install dependencies
pip install watchdog

# Run the application
python x32_scene_monitor.py

# Configure connection and select scene file
# Start monitoring for automatic updates
```

### **Configuration**
1. **Set X32 IP address** in connection settings
2. **Select scene file** to monitor
3. **Enable OSC** on X32 console
4. **Start monitoring** for automatic updates
5. **Verify connection** and file monitoring status

---

*This application provides seamless integration between scene file editing and real-time X32 console control, enabling efficient workflows for live sound, recording, and system integration scenarios.* 