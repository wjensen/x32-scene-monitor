# Changelog

All notable changes to the X32 Scene File Monitor project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure
- Basic documentation
- GitHub repository setup

## [1.0.0] - 2024-01-XX

### Added
- **Core Scene File Monitoring**
  - Real-time file watching with watchdog library
  - MD5 hash-based change detection
  - Debounced file change processing (1-second debounce)
  - Cross-platform file system monitoring

- **X32 Console Integration**
  - OSC protocol communication
  - Direct parameter application to console
  - Configurable IP address and port settings
  - Connection status monitoring and error handling

- **Scene File Parsing**
  - ASCII text parsing of .scn files
  - Regular expression-based parameter extraction
  - Support for channel, bus, main, and effects parameters
  - Structured data organization by parameter type

- **Change Detection & Application**
  - Before/after state comparison
  - Specific parameter change identification
  - Automatic OSC command generation
  - Success/failure logging for each change

- **User Interface**
  - Tkinter-based GUI application
  - Connection management controls
  - File selection and monitoring controls
  - Real-time status logging
  - Change history display

- **Supported X32 Parameters**
  - Channel faders (-60dB to +10dB)
  - Channel mutes (ON/OFF states)
  - Channel names (text changes)
  - Channel pan (-100 to +100)
  - Bus faders and mutes
  - Main stereo fader and mute
  - Effects parameters and types
  - Routing configurations

### Technical Features
- **OSC Protocol Implementation**
  - Proper OSC message formatting
  - Type tag generation (int, float, string, boolean)
  - Message encoding and transmission
  - UDP socket management

- **Error Handling & Safety**
  - Network connection failure handling
  - File parsing error recovery
  - Invalid parameter value validation
  - File system access error handling

- **Performance Optimization**
  - Efficient scene file parsing
  - Memory management for long-running sessions
  - Background file monitoring
  - Debounced change detection

### Documentation
- Comprehensive README.md with installation and usage instructions
- Detailed feature documentation in X32_Scene_Monitor_Features.md
- X32 scene file format documentation
- OSC protocol reference and examples
- Troubleshooting guide

### Project Structure
- Professional GitHub repository setup
- MIT License for open source distribution
- Contributing guidelines for community development
- Setup.py for pip installation
- Requirements.txt with dependency management
- .gitignore for Python project exclusions

## [0.1.0] - 2024-01-XX

### Added
- Initial concept and design
- Basic OSC communication framework
- Scene file parsing foundation
- GUI application prototype

---

## Version History

### Version 1.0.0
- **Release Date**: January 2024
- **Status**: Initial Release
- **Features**: Complete scene file monitoring and X32 integration
- **Compatibility**: Python 3.7+, X32 consoles with OSC enabled

### Version 0.1.0
- **Release Date**: January 2024
- **Status**: Development Prototype
- **Features**: Basic functionality proof of concept
- **Compatibility**: Python 3.7+

---

## Future Roadmap

### Version 1.1.0 (Planned)
- Enhanced EQ parameter monitoring and application
- Dynamics processing parameter changes
- Effects rack full parameter control
- Improved error handling and recovery

### Version 1.2.0 (Planned)
- Multi-file monitoring support
- Change scheduling capabilities
- Conditional change logic
- Advanced parameter validation

### Version 2.0.0 (Planned)
- Web interface for remote access
- Mobile app for iOS/Android
- Voice control integration
- Multi-console synchronization

---

## Migration Guide

### From Version 0.1.0 to 1.0.0
- No breaking changes
- Enhanced feature set
- Improved stability and error handling
- Better documentation and examples

---

## Known Issues

### Version 1.0.0
- Limited EQ parameter support (planned for 1.1.0)
- No multi-file monitoring (planned for 1.2.0)
- Basic effects parameter support (enhanced in 1.1.0)

---

## Acknowledgments

- **Behringer** for the X32 platform and OSC protocol
- **Python Community** for excellent libraries and tools
- **Open Source Contributors** for inspiration and guidance
- **X32 User Community** for feedback and testing 