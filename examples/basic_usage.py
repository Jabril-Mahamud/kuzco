#!/usr/bin/env python3
"""
Basic usage examples for AI CLI Assistant
"""
import subprocess
import sys
from pathlib import Path

def run_ai_cli_command(command):
    """Run an AI CLI command and return the output"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"

def example_chat():
    """Example of using AI CLI in chat mode"""
    print("=== Chat Mode Example ===")
    print("Starting AI CLI in chat mode...")
    print("Type 'exit' to quit the chat")

    # This would normally be interactive
    command = "python main.py --chat"
    returncode, stdout, stderr = run_ai_cli_command(command)

    if returncode == 0:
        print("Chat session completed successfully")
    else:
        print(f"Chat session failed: {stderr}")

def example_file_analysis():
    """Example of analyzing a file"""
    print("\n=== File Analysis Example ===")

    # Create a sample file to analyze
    sample_file = Path("sample_code.py")
    sample_content = '''
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(10))
'''

    sample_file.write_text(sample_content)

    command = f"python main.py --read {sample_file} --prompt 'Analyze this code and suggest improvements'"
    returncode, stdout, stderr = run_ai_cli_command(command)

    if returncode == 0:
        print("File analysis completed successfully")
        print(stdout)
    else:
        print(f"File analysis failed: {stderr}")

    # Clean up
    sample_file.unlink()

def example_system_assistant():
    """Example of using system assistant"""
    print("\n=== System Assistant Example ===")

    command = "python main.py --system 'show me disk usage'"
    returncode, stdout, stderr = run_ai_cli_command(command)

    if returncode == 0:
        print("System assistant completed successfully")
        print(stdout)
    else:
        print(f"System assistant failed: {stderr}")

if __name__ == "__main__":
    print("AI CLI Assistant - Usage Examples")
    print("=" * 50)

    # Note: These examples require AI CLI to be properly configured
    # and Ollama to be running with models available

    print("Note: These examples require:")
    print("1. Ollama to be installed and running")
    print("2. At least one model to be available")
    print("3. Proper configuration in .env file")
    print()

    # Uncomment to run examples (requires setup)
    # example_chat()
    # example_file_analysis()
    # example_system_assistant()

    print("Examples ready to run when AI CLI is configured!")
