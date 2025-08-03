# Contributing to X32 Scene File Monitor

Thank you for your interest in contributing to the X32 Scene File Monitor project! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Bugs
- Use the [GitHub Issues](https://github.com/yourusername/x32-scene-monitor/issues) page
- Include detailed steps to reproduce the bug
- Provide your operating system and Python version
- Include any error messages or logs

### Suggesting Features
- Use the [GitHub Issues](https://github.com/yourusername/x32-scene-monitor/issues) page
- Describe the feature and its use case
- Explain how it would benefit users
- Consider implementation complexity

### Code Contributions
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 🛠️ Development Setup

### Prerequisites
- Python 3.7 or higher
- Git
- X32 console (for testing)

### Local Development
```bash
# Clone the repository
git clone https://github.com/yourusername/x32-scene-monitor.git
cd x32-scene-monitor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Running Tests
```bash
# Run basic tests (when implemented)
python -m pytest

# Run with coverage
python -m pytest --cov=x32_scene_monitor
```

## 📝 Code Style

### Python Style Guide
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines
- Use meaningful variable and function names
- Add docstrings to all public functions and classes
- Keep functions focused and concise

### Code Formatting
- Use 4 spaces for indentation
- Maximum line length of 88 characters
- Use type hints where appropriate
- Follow the existing code structure

### Documentation
- Update README.md for user-facing changes
- Add docstrings for new functions and classes
- Update feature documentation as needed
- Include examples for new features

## 🧪 Testing

### Test Requirements
- Write tests for new features
- Ensure existing tests pass
- Test on multiple platforms if possible
- Test with different X32 configurations

### Test Structure
```python
def test_feature_name():
    """Test description of what is being tested."""
    # Arrange
    # Act
    # Assert
```

## 🔧 X32 Testing

### Console Setup
- Enable OSC on your X32 console
- Configure network settings
- Test with sample scene files
- Verify parameter changes are applied correctly

### Test Scenarios
- File monitoring with various scene files
- Network connection handling
- Parameter change detection
- Error handling and recovery

## 📋 Pull Request Guidelines

### Before Submitting
- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation is updated
- [ ] No new warnings or errors
- [ ] Feature is tested with X32 console

### Pull Request Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Code refactoring

## Testing
- [ ] Tested locally
- [ ] Tested with X32 console
- [ ] All tests pass

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes
```

## 🚀 Release Process

### Version Numbers
- Follow [Semantic Versioning](https://semver.org/)
- Major version for breaking changes
- Minor version for new features
- Patch version for bug fixes

### Release Checklist
- [ ] Update version in setup.py
- [ ] Update CHANGELOG.md
- [ ] Run all tests
- [ ] Test with X32 console
- [ ] Create release tag
- [ ] Update documentation

## 📞 Getting Help

### Communication Channels
- [GitHub Issues](https://github.com/yourusername/x32-scene-monitor/issues)
- [GitHub Discussions](https://github.com/yourusername/x32-scene-monitor/discussions)

### Resources
- [X32 OSC Protocol Documentation](https://behringer.com/x32/docs)
- [Python Documentation](https://docs.python.org/)
- [OSC Protocol Specification](http://opensoundcontrol.org/)

## 📄 License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.

## 🙏 Acknowledgments

Thank you to all contributors who help improve this project for the X32 community! 