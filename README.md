# ZenCode Terminal Application

## Overview
ZenCode is a terminal-based AI coding assistant that communicates with Ollama servers to generate code, create files, and execute shell commands directly from your command line. It provides a Claude Code-like experience while being fully customizable for remote Ollama deployments.

## Features
- **Remote Ollama Support**: Connects to any Ollama server (local or remote)
- **Model Selection**: Choose from all available Ollama models
- **File Creation**: Automatically creates files in your current working directory
- **Directory Management**: Creates directories when instructed by the AI
- **Command Execution**: Safely executes shell commands from AI responses
- **Keyboard History**: Use arrow keys to navigate and edit previous prompts
- **Error Handling**: Comprehensive error reporting and safety measures
- **Auto-save Feature**: Optional automatic code block saving
- **Command Logging**: Optional logging of executed commands
- **Batch Execution Control**: "Execute all" or "Skip all" options
- **Configuration File Support**: Store preferences and default settings

## Installation

### Prerequisites
- Python 3.6+
- pip (Python package installer)

### Setup Instructions

1. **Create the application directory:**
```bash
mkdir -p ~/zen-code-app
cd ~/zen-code-app
```

2. **Download the main script:**
```bash
wget https://github.com/lazydave-droid/ZenCode/blob/main/zen_code.py
chmod +x zen_code.py
```

3. **Create launcher script:**
```bash
nano run_zen.sh
```

Add the following content:
```bash
#!/bin/bash

# Navigate to the app directory
cd ~/zen-code-app

# Check if Python is available
if command -v python3 &> /dev/null; then
    python3 zen_code.py "$@"
elif command -v python &> /dev/null; then
    python zen_code.py "$@"
else
    echo "Error: Python not found. Please install Python 3."
    exit 1
fi
```

Make it executable:
```bash
chmod +x run_zen.sh
```

### Virtual Environment Setup (Recommended)

To avoid system-wide package installations:

```bash
# Create virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install required packages
pip install requests

# Deactivate when done (optional)
deactivate
```

## Usage

### Basic Usage
```bash
# Run with default local Ollama server
./run_zen.sh

# Run with remote Ollama server
./run_zen.sh --ollama-url http://your-remote-server:11434

# Run with custom port
./run_zen.sh --ollama-url http://localhost:11435
```

### Example Prompts

1. **Simple file creation:**
```
Create a Python script that calculates factorial using recursion. Save it as factorial.py.
```

2. **Web application generation:**
```
Generate a complete web application with HTML, CSS, and JavaScript that displays a to-do list. Create separate files for each component in a directory called todo_app.
```

3. **Directory and file operations:**
```
Create a directory called test_dir and put a file named test.txt inside it with the content "Hello World".
```

## Configuration

### Command Line Arguments
- `--ollama-url` (optional): Ollama server URL (default: `http://localhost:11434`)

### Working Directory Behavior
ZenCode operates from wherever you run it:
```bash
# Create new folder and run from there
mkdir -p /home/bob/newfolder
cd /home/bob/newfolder
~/zen-code-app/run_zen.sh
```
All file operations will be relative to this current directory.

### Configuration File Support
Create `~/.zenconfig` for persistent settings:
```json
{
    "ollama_url": "http://localhost:11434",
    "auto_save": true,
    "log_commands": false,
    "default_model": "llama3:8b"
}
```

## Security Considerations

1. **Command Execution Safety**: All shell commands must be manually confirmed before execution
2. **Warning System**: Large command batches (>10) trigger warnings
3. **Error Reporting**: Detailed error messages for failed commands
4. **No Automatic File Creation**: Code blocks are shown but not automatically saved to prevent clutter

## Troubleshooting

### Common Issues

**Python Environment Error:**
```
error: externally-managed-environment
```

**Solution:** Use a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install requests
```

**Ollama Connection Issues:**
- Verify Ollama server is running
- Check network connectivity to the Ollama URL
- Ensure proper port forwarding if using remote servers

### Keyboard Navigation
- Use arrow keys to navigate through command history
- Edit previous prompts before submitting
- Press Tab for auto-completion where supported

## Enhanced Features Implementation

### Auto-save Feature
```bash
# Enable auto-save in configuration file
{
    "auto_save": true
}
```

When enabled, code blocks will be automatically saved with timestamps:
```
generated_20260624_080134.py
generated_20260624_080134.js
```

### Command Logging
```bash
# Enable logging in configuration file
{
    "log_commands": true
}
```

Logs are saved to `~/.zen-code/logs/` with timestamps.

### Batch Execution Control
When >10 commands detected:
```
Found 15 shell command(s) in response:
  1. mkdir project_dir
  2. echo "Hello" > project_dir/test.txt
  ...
Execute these commands? (y/n/a/s) 
```

Options:
- `y` - Execute all commands
- `n` - Cancel execution
- `a` - Execute all without confirmation
- `s` - Skip all commands

## Development Roadmap

### Current Features Implemented:
1. ✅ Remote Ollama server support
2. ✅ Model selection interface
3. ✅ File and directory creation
4. ✅ Shell command execution with confirmation
5. ✅ Keyboard history support
6. ✅ Error handling and safety measures
7. ✅ Auto-save feature
8. ✅ Command logging
9. ✅ Batch execution control
10. ✅ Configuration file support

### Future Enhancements:
1. **Enhanced Prompt Templates**: Predefined templates for common tasks
2. **File Comparison Tools**: Compare generated files with existing ones
3. **Project Scaffolding**: Create complete project structures with multiple files
4. **Version Control Integration**: Git integration for tracking changes
5. **Collaborative Mode**: Share and collaborate on code generation sessions

## License
MIT License - Free to use, modify, and distribute.

---

*Note: This tool requires an active Ollama server to function. Ensure your Ollama installation is running and accessible before using ZenCode.*
