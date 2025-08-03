# Sample Files

This directory contains sample X32 scene files and configuration files that demonstrate how to use the X32 Scene File Monitor application.

## 📁 **Sample Files**

### **Scene Files (.scn)**

#### **`sample_x32_rack_scene.scn`**
- **Type**: X32 Rack scene file
- **Description**: Complete X32 Rack configuration with 6 analog inputs
- **Features**:
  - 32 input channels with names and settings
  - 16 mix buses (monitor mixes, floor monitors, effects sends)
  - 8 effects processors
  - Main stereo output routing
  - DCA groups and assignments
- **Use Case**: Perfect for testing with X32 Rack consoles
- **Key Parameters**:
  - Main fader: `0.0` (unmuted)
  - Main outputs: 1-2 (correct for X32 Rack)
  - Input routing: `AN1-6 CARD1-2 CARD3-4 CARD5-6 CARD7-8`

#### **`sample_venue_scene.scn`**
- **Type**: X32 venue scene file
- **Description**: Venue setup with monitor mixes and floor monitors
- **Features**:
  - Monitor bus configurations
  - Floor monitor routing
  - Channel assignments for band members
  - Effects and dynamics processing
- **Use Case**: Example of venue-specific configuration
- **Key Parameters**:
  - Floor Mon 1: Bus 9 → Output 7
  - Floor Mon 2: Bus 10 → Output 8
  - Monitor buses: Various configurations for different musicians

### **Channel Files (.chn)**

#### **`sample_room_setup.chn`**
- **Type**: X32 channel configuration file
- **Description**: Room-specific channel setup and routing
- **Features**:
  - Channel assignments for specific venue
  - Input/output routing configuration
  - Room-specific naming conventions
- **Use Case**: Example of venue-specific channel configuration

## 🎯 **How to Use These Samples**

### **1. Testing the Scene File Monitor**
```bash
# Copy a sample file to your working directory
cp samples/sample_x32_rack_scene.scn my_scene.scn

# Run the scene monitor
python x32_scene_monitor.py

# Select the scene file and start monitoring
# Make changes to my_scene.scn and watch them apply to X32
```

### **2. Learning Scene File Structure**
- **Open the .scn files** in a text editor to see the format
- **Study the parameter structure** to understand X32 scene files
- **Use as templates** for creating your own scenes

### **3. Understanding X32 Configuration**
- **Channel settings**: Names, faders, mutes, pan, EQ
- **Bus configurations**: Monitor mixes, effects sends
- **Routing assignments**: Input/output mapping
- **Effects processing**: Reverb, delay, compression

## 📋 **Sample File Analysis**

### **Key Sections in Scene Files**

#### **Channel Configuration**
```
/ch/01/config "Kick" 1 WHi
/ch/01/mix ON  +2.0 ON +8 OFF   -oo
/ch/01/mix/01 ON  +9.0 +0 EQ-> 0
```

#### **Bus Configuration**
```
/bus/01/config "Aaron Mon L" 53 WHi
/bus/01/mix ON -10.0 OFF -100 OFF   -oo
```

#### **Main Output**
```
/main/st/mix ON   0.0 +6
/outputs/main/01 1 POST OFF
/outputs/main/02 2 POST OFF
```

#### **Routing Configuration**
```
/config/routing/IN AN1-6 CARD1-2 CARD3-4 CARD5-6 CARD7-8
```

## 🔧 **Customizing Samples**

### **For Your X32 Rack**
1. **Copy the sample file**: `cp samples/sample_x32_rack_scene.scn my_setup.scn`
2. **Edit channel names**: Update for your instruments
3. **Adjust routing**: Match your input/output setup
4. **Modify monitor mixes**: Configure for your musicians
5. **Test with scene monitor**: Apply changes automatically

### **For Different Venues**
1. **Use venue sample**: `cp samples/sample_venue_scene.scn venue_setup.scn`
2. **Update room configuration**: Modify for specific venue
3. **Adjust monitor assignments**: Configure for different bands
4. **Test routing**: Ensure all connections work

## ⚠️ **Important Notes**

### **File Format**
- **Scene files (.scn)**: ASCII text format, editable in any text editor
- **Channel files (.chn)**: X32 channel configuration format
- **Backup your files**: Always keep backups before making changes

### **Testing**
- **Test in safe environment**: Use samples before applying to live console
- **Verify connections**: Ensure X32 routing matches your setup
- **Monitor levels**: Check that changes don't cause feedback or overload

### **Customization**
- **Parameter ranges**: Respect X32 parameter limits
- **OSC addresses**: Use correct OSC paths for your X32 model
- **Network settings**: Ensure proper IP configuration

## 🎛️ **Example Workflow**

### **Using Sample with Scene Monitor**
1. **Select sample file** in the scene monitor
2. **Start monitoring** for automatic detection
3. **Edit the file** (manually or via AI assistance)
4. **Watch changes apply** to X32 console automatically
5. **Verify results** in the monitor interface

### **Learning from Samples**
1. **Study the structure** of sample files
2. **Identify patterns** in parameter formatting
3. **Understand routing** configurations
4. **Practice modifications** on copies
5. **Apply knowledge** to your own setups

---

These sample files provide real-world examples of X32 configurations and help users understand how to work with scene files and the X32 Scene File Monitor application. 