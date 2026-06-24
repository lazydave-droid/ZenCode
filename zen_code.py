#!/usr/bin/env python3
# File: zen_code.py

import os
import sys
import json
import subprocess
import requests
from datetime import datetime
import argparse
import re
import readline
import logging

class ZenCode:
    def __init__(self, ollama_url="http://localhost:11434"):
        self.ollama_url = ollama_url
        self.models = []
        self.current_model = None
        self.working_dir = os.getcwd()
        self.config = self.load_config()
        
    def load_config(self):
        """Load configuration from file or return defaults"""
        config = {
            "ollama_url": "http://localhost:11434",
            "auto_save": False,
            "log_commands": False,
            "default_model": None
        }
        
        try:
            config_file = os.path.expanduser("~/.zenconfig")
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    file_config = json.load(f)
                    config.update(file_config)
        except Exception as e:
            print(f"Warning: Could not load config file: {e}")
            
        return config
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            config_file = os.path.expanduser("~/.zenconfig")
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config file: {e}")
    
    def get_available_models(self):
        """Get list of available models from Ollama"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                self.models = [model['name'] for model in data.get('models', [])]
                return self.models
            else:
                print(f"Error fetching models: {response.status_code}")
                return []
        except Exception as e:
            print(f"Error connecting to Ollama at {self.ollama_url}: {e}")
            return []
    
    def select_model(self):
        """Allow user to select a model"""
        if not self.models:
            print("No models found. Please check your Ollama installation.")
            return None
            
        print("\nAvailable models:")
        for i, model in enumerate(self.models, 1):
            print(f"{i}. {model}")
        
        while True:
            try:
                choice = input(f"\nSelect a model (1-{len(self.models)}): ")
                index = int(choice) - 1
                if 0 <= index < len(self.models):
                    self.current_model = self.models[index]
                    print(f"Selected model: {self.current_model}")
                    
                    # Save as default if not already set
                    if not self.config.get('default_model'):
                        self.config['default_model'] = self.current_model
                        self.save_config()
                    
                    return self.current_model
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
    
    def get_model_info(self, model_name):
        """Get detailed information about a specific model"""
        try:
            response = requests.get(f"{self.ollama_url}/api/show", 
                                 json={"name": model_name})
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error getting model info: {e}")
            return None
    
    def send_prompt(self, prompt):
        """Send prompt to Ollama and get response"""
        if not self.current_model:
            print("No model selected!")
            return None
            
        payload = {
            "model": self.current_model,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            response = requests.post(f"{self.ollama_url}/api/generate", 
                                  json=payload, timeout=300)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('response', '')
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error communicating with Ollama at {self.ollama_url}: {e}")
            return None
    
    def execute_shell_command(self, command):
        """Execute shell commands safely"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=300)
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_file(self, filename, content):
        """Create a file in the current working directory"""
        try:
            filepath = os.path.join(self.working_dir, filename)
            
            # Create parent directories if needed
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w') as f:
                f.write(content)
            
            return filepath
            
        except Exception as e:
            print(f"✗ Error creating file: {e}")
            return None
    
    def log_command(self, command, success):
        """Log executed commands if logging is enabled"""
        if not self.config.get('log_commands', False):
            return
            
        try:
            log_dir = os.path.expanduser("~/.zen-code/logs")
            os.makedirs(log_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = os.path.join(log_dir, f"command_{timestamp}.log")
            
            with open(log_file, 'w') as f:
                f.write(f"Command: {command}\n")
                f.write(f"Success: {success}\n")
                f.write(f"Timestamp: {datetime.now()}\n")
                f.write(f"Working Directory: {self.working_dir}\n")
                
        except Exception as e:
            print(f"Warning: Could not log command: {e}")
    
    def handle_file_creation(self, response):
        """Parse response and create files if commands are found"""
        # Look for shell commands in the response
        lines = response.split('\n')
        command_lines = []
        
        # Extract potential shell commands
        for line in lines:
            line = line.strip()
            # Look for common file creation patterns
            if (line.startswith('cat > ') or 
                line.startswith('echo ') or 
                line.startswith('mkdir ') or
                line.startswith('cp ') or
                line.startswith('touch ')):
                command_lines.append(line)
        
        if command_lines:
            print(f"\nFound {len(command_lines)} shell command(s) in response:")
            for i, cmd in enumerate(command_lines, 1):
                print(f"  {i}. {cmd}")
            
            # Show a warning about potentially many commands
            if len(command_lines) > 10:
                print(f"\n⚠️  Warning: This will execute {len(command_lines)} commands!")
                print("Options: (y) Execute all, (n) Cancel, (a) Execute all without confirmation, (s) Skip all")
                choice = input("Choose option (y/n/a/s): ").lower()
            else:
                choice = input("\nExecute these commands? (y/n): ").lower()
                
            if choice == 'y' or choice == 'a':
                executed_count = 0
                for i, cmd in enumerate(command_lines, 1):
                    print(f"Executing command {i}/{len(command_lines)}: {cmd}")
                    result = self.execute_shell_command(cmd)
                    self.log_command(cmd, result['success'])
                    if result['success']:
                        print(f"  ✓ Command {i} completed successfully")
                        executed_count += 1
                    else:
                        print(f"  ✗ Command {i} failed:")
                        if result.get('stderr'):
                            print(f"    Error: {result['stderr']}")
                        elif result.get('error'):
                            print(f"    Error: {result['error']}")
                
                print(f"\n✅ Completed: {executed_count}/{len(command_lines)} commands executed successfully")
            elif choice == 's':
                print("❌ Commands execution skipped")
            else:
                print("❌ Commands execution cancelled")
        else:
            print("\nNo shell commands found in response")
        
        # Check for code blocks and show them
        if '```' in response:
            pattern = r'```([a-zA-Z0-9]+)\n(.*?)```'
            matches = re.findall(pattern, response, re.DOTALL)
            
            if matches:
                print(f"\nFound {len(matches)} code block(s) in response:")
                for i, (lang, code) in enumerate(matches, 1):
                    print(f"  Code block {i} ({lang}):")
                    # Show first few lines of each code block
                    lines = code.split('\n')[:10]
                    for line in lines:
                        print(f"    {line}")
                    if len(lines) < len(code.split('\n')):
                        print("    ... (truncated)")
                
                # Auto-save feature
                if self.config.get('auto_save', False):
                    print("\n💾 Auto-saving code blocks...")
                    for i, (lang, code) in enumerate(matches, 1):
                        filename = f"generated_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}.{self.get_file_extension(lang)}"
                        if self.create_file(filename, code):
                            print(f"  ✓ Saved to {filename}")
    
    def get_file_extension(self, language):
        """Get appropriate file extension for programming language"""
        extensions = {
            'python': 'py',
            'javascript': 'js',
            'java': 'java',
            'cpp': 'cpp',
            'c': 'c',
            'html': 'html',
            'css': 'css',
            'bash': 'sh',
            'sh': 'sh',
            'sql': 'sql'
        }
        return extensions.get(language.lower(), 'txt')
    
    def chat(self):
        """Main chat loop"""
        print("ZenCode Terminal App")
        print("=" * 30)
        
        # Get available models
        self.models = self.get_available_models()
        if not self.models:
            print("No models found. Please ensure Ollama is running.")
            return
        
        # Select model (use default if configured)
        if self.config.get('default_model') and len(self.models) > 0:
            print(f"Using default model: {self.config['default_model']}")
            self.current_model = self.config['default_model']
        else:
            if not self.select_model():
                return
            
        print(f"\nCurrent working directory: {self.working_dir}")
        print("Type 'quit' or 'exit' to end the session")
        print("Type 'help' for available commands")
        print("Type 'list_models' to see available models")
        print("Type 'switch_model' to change model")
        print("Type 'auto_save' to toggle auto-save feature")
        print("Type 'log_commands' to toggle command logging")
        print("-" * 30)
        
        while True:
            try:
                user_input = input("\n> ").strip()
                
                if user_input.lower() in ['quit', 'exit']:
                    print("Goodbye!")
                    break
                elif user_input.lower() == 'help':
                    print("Available commands:")
                    print("- quit/exit: Exit the application")
                    print("- help: Show this help")
                    print("- list_models: List available models")
                    print("- switch_model: Change current model")
                    print("- auto_save: Toggle auto-save feature")
                    print("- log_commands: Toggle command logging")
                    print("- pwd: Show current directory")
                    print("- files: List files in current directory")
                elif user_input.lower() == 'list_models':
                    self.get_available_models()
                    for i, model in enumerate(self.models, 1):
                        print(f"{i}. {model}")
                elif user_input.lower() == 'switch_model':
                    self.select_model()
                elif user_input.lower() == 'auto_save':
                    self.config['auto_save'] = not self.config['auto_save']
                    print(f"Auto-save: {'Enabled' if self.config['auto_save'] else 'Disabled'}")
                    self.save_config()
                elif user_input.lower() == 'log_commands':
                    self.config['log_commands'] = not self.config['log_commands']
                    print(f"Command logging: {'Enabled' if self.config['log_commands'] else 'Disabled'}")
                    self.save_config()
                elif user_input.lower() == 'pwd':
                    print(f"Current directory: {self.working_dir}")
                elif user_input.lower() == 'files':
                    files = os.listdir(self.working_dir)
                    for f in sorted(files):
                        filepath = os.path.join(self.working_dir, f)
                        if os.path.isfile(filepath):
                            size = os.path.getsize(filepath)
                            print(f"  {f} ({size} bytes)")
                        else:
                            print(f"  {f}/")
                else:
                    # Send to Ollama
                    prompt = user_input
                    
                    print("\nThinking...")
                    response = self.send_prompt(prompt)
                    
                    if response:
                        print("\n" + "="*50)
                        print("Response:")
                        print("="*50)
                        print(response)
                        print("="*50)
                        
                        # Handle file creation
                        self.handle_file_creation(response)
                        print("\n✅ Processing complete - back to prompt")
                    else:
                        print("No response received from model.")
                        
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(description='ZenCode Terminal App')
    parser.add_argument('--ollama-url', default='http://localhost:11434',
                       help='Ollama server URL (default: http://localhost:11434)')
    
    args = parser.parse_args()
    
    app = ZenCode(args.ollama_url)
    app.chat()

if __name__ == "__main__":
    main()
