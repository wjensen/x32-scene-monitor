# Project Structure

This document provides an overview of the X32 Scene File Monitor project structure and organization.

## 📁 **Repository Overview**

```
x32-scene-monitor/
├── 📄 Core Application Files
│   ├── x32_scene_monitor.py          # Main application (Scene File Monitor)
│   ├── x32_remote_control.py         # Basic remote control application
│   └── x32_advanced_remote.py        # Advanced remote control with tabs
│
├── 📋 Configuration & Dependencies
│   ├── requirements.txt              # Python dependencies
│   ├── setup.py                      # Package installation configuration
│   └── .gitignore                    # Git ignore rules
│
├── 📚 Documentation
│   ├── README.md                     # Main project documentation
│   ├── X32_Scene_Monitor_Features.md # Detailed feature documentation
│   ├── scn_file_documentation.txt    # X32 scene file format guide
│   ├── CONTRIBUTING.md               # Contribution guidelines
│   ├── CHANGELOG.md                  # Version history and changes
│   └── PROJECT_STRUCTURE.md          # This file
│
├── 🔧 Development & CI/CD
│   ├── .github/
│   │   └── workflows/
│   │       └── ci.yml                # GitHub Actions CI/CD pipeline
│   └── LICENSE                       # MIT License
│
└── 📁 Example Files (Optional)
    └── X32_Rack.scn                  # Example X32 scene file
```

## 🎯 **Core Application Files**

### **`x32_scene_monitor.py`** - Main Application
- **Purpose**: Scene file monitoring and automatic X32 control
- **Key Features**:
  - Real-time file watching with watchdog
  - Scene file parsing and change detection
  - OSC communication with X32 console
  - GUI interface for monitoring and control
- **Usage**: Primary application for scene file monitoring workflow

### **`x32_remote_control.py`** - Basic Remote Control
- **Purpose**: Simple X32 remote control interface
- **Key Features**:
  - Basic fader and mute controls
  - Channel and bus management
  - Simple GUI interface
- **Usage**: Alternative to X32-Edit for basic remote control

### **`x32_advanced_remote.py`** - Advanced Remote Control
- **Purpose**: Enhanced X32 remote control with advanced features
- **Key Features**:
  - Tabbed interface for organization
  - Scene management capabilities
  - Pan controls and effects framework
  - Menu system for file operations
- **Usage**: Advanced remote control with scene management

## 📋 **Configuration Files**

### **`requirements.txt`** - Dependencies
```txt
# Required dependencies for scene monitoring
watchdog>=2.1.0      # File system monitoring

# Optional dependencies for enhanced functionality
# python-osc>=1.7.4  # Better OSC implementation
# numpy>=1.21.0      # For advanced audio processing
# matplotlib>=3.5.0  # For spectrum analysis and EQ visualization
# pyserial>=3.5      # For MIDI control surface support
```

### **`setup.py`** - Package Configuration
- **Purpose**: Makes the project installable via pip
- **Features**:
  - Package metadata and versioning
  - Dependency management
  - Console script entry points
  - PyPI distribution configuration

### **`.gitignore`** - Version Control
- **Purpose**: Excludes unnecessary files from Git
- **Includes**:
  - Python cache and build files
  - Virtual environments
  - IDE configuration files
  - OS-specific files
  - X32-specific backup files

## 📚 **Documentation Structure**

### **`README.md`** - Main Documentation
- **Purpose**: Primary project documentation and user guide
- **Content**:
  - Project overview and features
  - Installation and setup instructions
  - Usage examples and workflows
  - Troubleshooting guide
  - Contributing information

### **`X32_Scene_Monitor_Features.md`** - Feature Documentation
- **Purpose**: Comprehensive feature overview
- **Content**:
  - Detailed feature descriptions
  - Technical specifications
  - Use cases and workflows
  - Future enhancement roadmap

### **`scn_file_documentation.txt`** - Scene File Guide
- **Purpose**: X32 scene file format documentation
- **Content**:
  - Scene file structure analysis
  - Parameter format specifications
  - OSC protocol details
  - File format examples

### **`CONTRIBUTING.md`** - Contribution Guide
- **Purpose**: Guidelines for project contributors
- **Content**:
  - How to contribute code
  - Development setup instructions
  - Code style guidelines
  - Testing requirements
  - Pull request process

### **`CHANGELOG.md`** - Version History
- **Purpose**: Track project changes and releases
- **Content**:
  - Version history with dates
  - Feature additions and changes
  - Bug fixes and improvements
  - Migration guides
  - Future roadmap

## 🔧 **Development Infrastructure**

### **`.github/workflows/ci.yml`** - CI/CD Pipeline
- **Purpose**: Automated testing and quality assurance
- **Features**:
  - Multi-platform testing (Windows, macOS, Linux)
  - Multiple Python version support (3.7-3.11)
  - Code linting and formatting checks
  - Test coverage reporting
  - Package building and distribution

### **`LICENSE`** - Open Source License
- **Type**: MIT License
- **Purpose**: Allows free use, modification, and distribution
- **Benefits**: Permissive license for commercial and personal use

## 🎯 **Application Architecture**

### **Core Components**

#### **SceneParser Class**
```python
class SceneParser:
    """Parse and apply X32 scene file changes"""
    - parse_scene_file()      # Parse .scn files
    - detect_changes()        # Compare scene states
    - _parse_channel_line()   # Parse channel parameters
    - _parse_bus_line()       # Parse bus parameters
```

#### **X32Connection Class**
```python
class X32Connection:
    """X32 console connection and control"""
    - connect()               # Establish connection
    - send_message()          # Send OSC commands
    - apply_changes()         # Apply detected changes
    - _create_osc_message()   # Format OSC messages
```

#### **SceneFileHandler Class**
```python
class SceneFileHandler(FileSystemEventHandler):
    """File system event handler"""
    - on_modified()           # Handle file changes
    - debounced updates       # Prevent rapid changes
```

#### **X32SceneMonitor Class**
```python
class X32SceneMonitor:
    """Main application"""
    - setup_gui()             # Create user interface
    - toggle_monitoring()     # Start/stop monitoring
    - on_scene_file_changed() # Handle file changes
    - display_changes()       # Show change history
```

## 🚀 **Usage Workflows**

### **Primary Workflow (Scene File Monitoring)**
1. **Setup**: Configure X32 connection and select scene file
2. **Monitor**: Start file monitoring for automatic detection
3. **Edit**: Modify scene file (manually or via AI)
4. **Apply**: Changes automatically apply to X32 console
5. **Verify**: Monitor interface shows applied changes

### **Alternative Workflow (Direct Remote Control)**
1. **Connect**: Establish connection to X32 console
2. **Control**: Use GUI controls for direct parameter adjustment
3. **Monitor**: View real-time status and changes
4. **Save**: Optionally save changes to scene file

## 🔄 **Integration Points**

### **External Tools**
- **X32-Edit**: Compatible scene file editing
- **Text Editors**: Any text editor for scene file modification
- **Version Control**: Git integration for scene file versioning
- **Backup Systems**: Automated scene file backups

### **Automation**
- **Scripts**: Python, batch, or shell script integration
- **Scheduling**: Cron jobs or task scheduler integration
- **APIs**: REST API integration for web applications
- **Databases**: Scene parameter storage and retrieval

## 📈 **Future Structure**

### **Planned Additions**
```
x32-scene-monitor/
├── 📁 tests/                    # Test suite
│   ├── test_scene_parser.py
│   ├── test_x32_connection.py
│   └── test_gui.py
│
├── 📁 docs/                     # Enhanced documentation
│   ├── api/                     # API documentation
│   ├── tutorials/               # Step-by-step guides
│   └── examples/                # Code examples
│
├── 📁 examples/                 # Example files
│   ├── sample_scenes/           # Sample scene files
│   ├── scripts/                 # Utility scripts
│   └── configs/                 # Configuration examples
│
└── 📁 web/                      # Web interface (future)
    ├── static/                  # Web assets
    ├── templates/               # HTML templates
    └── app.py                   # Flask web application
```

## 🎯 **Key Design Principles**

### **Modularity**
- **Separation of Concerns**: Each class has a specific responsibility
- **Loose Coupling**: Components can work independently
- **High Cohesion**: Related functionality grouped together

### **Extensibility**
- **Plugin Architecture**: Easy to add new features
- **Configuration Driven**: Settings externalized from code
- **API Design**: Clean interfaces for integration

### **Reliability**
- **Error Handling**: Comprehensive error management
- **Validation**: Input validation and parameter checking
- **Logging**: Detailed logging for debugging and monitoring

### **User Experience**
- **Intuitive Interface**: Easy-to-use GUI design
- **Real-time Feedback**: Immediate status updates
- **Comprehensive Documentation**: Clear usage instructions

---

This structure provides a solid foundation for the X32 Scene File Monitor project, enabling both current functionality and future growth while maintaining code quality and user experience. 