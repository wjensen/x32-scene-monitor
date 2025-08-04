# X32 OSC Protocol Implementation Guide

## 📋 **Overview**

This guide documents the implementation of the X32 OSC (Open Sound Control) protocol based on the official X32-OSC.pdf specifications. The implementation provides comprehensive control over all aspects of the X32/M32 digital mixing console family.

## 🎛️ **Protocol Basics**

### **OSC Communication**
- **Protocol**: OSC over UDP
- **Port**: 10023 (default)
- **Address Format**: `/category/subcategory/parameter`
- **Data Types**: String (s), Integer (i), Float (f), Blob (b)

### **Connection Modes**
1. **Immediate Mode**: Direct request/response
2. **Deferred Mode**: Remote control with continuous updates (`/xremote`)

## 🔧 **Core Classes**

### **X32OSCMessage**
Proper OSC message implementation with:
- Address pattern formatting
- Type tag generation
- Binary data conversion
- Null-padding for 4-byte boundaries

### **X32OSCConnection**
Complete X32 communication class with:
- Bidirectional OSC communication
- Message parsing and handling
- Callback registration system
- Meter data processing

### **X32OSCApp**
GUI application with:
- Tabbed interface for different functions
- Real-time control capabilities
- Scene management
- Effects control

## 📡 **OSC Address Patterns**

### **Channel Control (`/ch`)**
```
/ch/{channel:02d}/mix/fader     # Fader level (0.0-1.0)
/ch/{channel:02d}/mix/on        # Mute state (ON/OFF)
/ch/{channel:02d}/config/name   # Channel name
/ch/{channel:02d}/mix/pan       # Pan position (-1.0 to 1.0)
/ch/{channel:02d}/eq/1/gain     # EQ band 1 gain
/ch/{channel:02d}/dyn/on        # Dynamics on/off
/ch/{channel:02d}/dyn/mode      # Dynamics mode
```

### **Bus Control (`/bus`)**
```
/bus/{bus:02d}/mix/fader       # Bus fader level
/bus/{bus:02d}/mix/on          # Bus mute state
/bus/{bus:02d}/config/name     # Bus name
/bus/{bus:02d}/eq/1/gain       # Bus EQ band 1 gain
/bus/{bus:02d}/dyn/on          # Bus dynamics on/off
```

### **Main Stereo (`/main/st`)**
```
/main/st/mix/fader             # Main fader level
/main/st/mix/on                # Main mute state
/main/st/eq/1/gain             # Main EQ band 1 gain
/main/st/dyn/on                # Main dynamics on/off
```

### **Effects (`/fx`)**
```
/fx/{fx}/config/type           # Effects type
/fx/{fx}/par/{param}           # Effects parameter
/fx/{fx}/on                    # Effects on/off
```

### **Metering (`/meters`)**
```
/meters                        # Start meter streaming
/meters meters/1               # Input meters (32 channels)
/meters meters/2               # Gate meters (32 channels)
/meters meters/3               # Dynamic meters (32 channels)
```

### **Scene Management**
```
/-action/loadscene             # Load scene by number
/-action/savescene             # Save scene
/-show/scenes                  # Get scene list
/-show/snippets                # Get snippet list
```

### **Remote Control**
```
/xremote                       # Start remote control mode
/xremote ""                    # Stop remote control mode
```

## 🎯 **Implementation Features**

### **1. Proper OSC Message Formatting**
- Correct address pattern padding
- Type tag generation
- Argument serialization
- Binary blob handling

### **2. Bidirectional Communication**
- Send commands to X32
- Receive responses and updates
- Parse incoming OSC messages
- Handle meter data blobs

### **3. Real-time Control**
- Channel faders and mutes
- Bus controls
- Main stereo control
- Effects parameters
- Scene management

### **4. Meter Data Processing**
- Parse 96 float values (32 input + 32 gate + 32 dynamic)
- Real-time meter display
- Multiple meter types support

### **5. Scene Management**
- Load/save scenes
- Scene list retrieval
- Remote control mode
- Scene safety handling

## 🖥️ **GUI Application**

### **Tabbed Interface**
1. **Faders Tab**: Channel, bus, and main fader controls
2. **Meters Tab**: Real-time meter display
3. **Scenes Tab**: Scene management and remote control
4. **Effects Tab**: Effects type and parameter control

### **Connection Management**
- IP address and port configuration
- Connection status display
- Automatic reconnection handling

### **Real-time Updates**
- Live fader control
- Mute state toggles
- Meter data visualization
- Scene status updates

## 📊 **Data Types and Ranges**

### **Fader Levels**
- **Range**: 0.0 to 1.0
- **Type**: Float
- **Conversion**: Linear to dB mapping available

### **Pan Positions**
- **Range**: -1.0 to 1.0
- **Type**: Float
- **-1.0**: Full left, **0.0**: Center, **1.0**: Full right

### **EQ Parameters**
- **Gain**: -15.0 to +15.0 dB
- **Frequency**: 20 Hz to 20 kHz
- **Q Factor**: 0.3 to 10.0

### **Dynamics**
- **Threshold**: -60.0 to 0.0 dB
- **Ratio**: 1.0 to 20.0
- **Attack**: 0.02 to 2000.0 ms
- **Release**: 5.0 to 4000.0 ms

## 🔄 **Usage Examples**

### **Basic Channel Control**
```python
# Connect to X32
connection = X32OSCConnection("192.168.1.100", 10023)
connection.connect()

# Set channel 1 fader to 50%
connection.set_channel_fader(1, 0.5)

# Mute channel 2
connection.set_channel_mute(2, True)

# Set channel 3 name
connection.set_channel_name(3, "Kick")

# Set channel 4 pan to center
connection.set_channel_pan(4, 0.0)
```

### **Bus and Main Control**
```python
# Set bus 1 fader
connection.set_bus_fader(1, 0.7)

# Set main fader
connection.set_main_fader(0.8)

# Mute main
connection.set_main_mute(True)
```

### **Effects Control**
```python
# Set effects 1 type
connection.set_fx_type(1, "Hall Reverb")

# Set effects parameter
connection.set_fx_param(1, "Decay", 0.6)
```

### **Scene Management**
```python
# Load scene 5
connection.load_scene(5)

# Save scene
connection.save_scene(1, "My Scene")

# Start remote control
connection.start_remote()
```

### **Metering**
```python
# Start meter streaming
connection.start_meters("meters/1")

# Access meter data
input_levels = connection.meter_data['input']
gate_levels = connection.meter_data['gate']
dynamic_levels = connection.meter_data['dynamic']
```

## 🛠️ **Advanced Features**

### **Callback System**
```python
def on_fader_change(address, args):
    print(f"Fader changed: {address} = {args}")

# Register callback for specific address
connection.register_callback("/ch/01/mix/fader", on_fader_change)
```

### **Custom OSC Messages**
```python
# Send custom OSC message
connection.send_message("/custom/address", "parameter", 123, 0.5)
```

### **Batch Operations**
```python
# Multiple parameters in one message
connection.send_message("/ch/01/mix", "ON", 0.7, 0.0)  # on, fader, pan
```

## ⚠️ **Important Considerations**

### **Network Performance**
- UDP packet loss handling
- Buffer overflow prevention
- WiFi network limitations
- Real-time data streaming

### **Parameter Ranges**
- Validate all parameter values
- Respect X32 parameter limits
- Handle out-of-range values gracefully

### **Error Handling**
- Connection timeouts
- Invalid OSC messages
- Console state synchronization
- Network disconnection recovery

### **Threading**
- Non-blocking GUI updates
- Background message processing
- Thread-safe data access
- Proper cleanup on exit

## 🔗 **Integration with Scene Monitor**

The OSC protocol implementation integrates seamlessly with the scene file monitor:

1. **Real-time Control**: Direct console control via OSC
2. **Scene Application**: Apply scene file changes via OSC
3. **Bidirectional Sync**: Console ↔ Scene file synchronization
4. **Live Monitoring**: Real-time parameter updates

## 📚 **Resources**

### **Official Documentation**
- `X32-OSC.pdf`: Complete OSC protocol specifications
- `X32_OSC_Specifications.txt`: Extracted text version

### **Related Files**
- `x32_osc_protocol.py`: Complete implementation
- `x32_scene_monitor.py`: Scene file monitoring
- `samples/`: Example scene files for testing

### **External Tools**
- X32_Command: Terminal-based OSC utility
- X32 Live Toolbox: GUI-based OSC utility
- GitHub: Open-source X32 tools

## 🚀 **Future Enhancements**

### **Planned Features**
- MIDI integration
- AES50 routing control
- P16 personal monitor control
- Advanced effects presets
- Multi-console support
- Web interface

### **Performance Optimizations**
- Message batching
- Compression for large data
- Caching for frequently accessed parameters
- Background synchronization

---

This implementation provides a complete, specification-compliant interface to the X32/M32 console family, enabling full remote control and automation capabilities. 