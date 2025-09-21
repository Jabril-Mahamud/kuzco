#!/bin/bash

# AI CLI Installation Script
# This script automates the installation and PATH setup for AI CLI

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python() {
    if command_exists python3; then
        PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
            print_success "Python $PYTHON_VERSION found (✓ >= 3.8)"
            return 0
        else
            print_error "Python $PYTHON_VERSION found, but version 3.8+ is required"
            return 1
        fi
    else
        print_error "Python 3 not found. Please install Python 3.8+ first."
        return 1
    fi
}

# Function to check Ollama
check_ollama() {
    if command_exists ollama; then
        print_success "Ollama found"
        # Check if Ollama is running
        if ollama list >/dev/null 2>&1; then
            print_success "Ollama is running"
        else
            print_warning "Ollama is installed but not running. Starting Ollama..."
            ollama serve &
            sleep 3
            if ollama list >/dev/null 2>&1; then
                print_success "Ollama started successfully"
            else
                print_error "Failed to start Ollama. Please start it manually: ollama serve"
                return 1
            fi
        fi
    else
        print_warning "Ollama not found. Installing Ollama..."
        curl -fsSL https://ollama.com/install.sh | sh
        if command_exists ollama; then
            print_success "Ollama installed successfully"
            print_status "Starting Ollama service..."
            ollama serve &
            sleep 3
        else
            print_error "Failed to install Ollama. Please install it manually."
            return 1
        fi
    fi
}

# Function to install AI CLI
install_ai_cli() {
    print_status "Installing AI CLI..."

    # Check if we're in the right directory
    if [ ! -f "setup.py" ] || [ ! -f "main.py" ]; then
        print_error "Please run this script from the AI CLI project directory"
        exit 1
    fi

    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv venv
    fi

    # Activate virtual environment
    print_status "Activating virtual environment..."
    source venv/bin/activate

    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip

    # Install requirements
    print_status "Installing dependencies..."
    pip install -r requirements.txt

    # Install in development mode
    print_status "Installing AI CLI in development mode..."
    pip install -e .

    print_success "AI CLI installed successfully"
}

# Function to setup configuration
setup_config() {
    print_status "Setting up configuration..."

    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_success "Configuration file created from .env.example"
        else
            print_warning "No .env.example found. You may need to create .env manually"
        fi
    else
        print_success "Configuration file already exists"
    fi
}

# Function to add to PATH
add_to_path() {
    print_status "Adding AI CLI to PATH..."

    # Check if ai-cli command is available
    if command_exists ai-cli; then
        print_success "AI CLI is already available in PATH"
        return 0
    fi

    # Get the current directory
    CURRENT_DIR=$(pwd)

    # Create a wrapper script
    WRAPPER_SCRIPT="$HOME/bin/ai-cli"
    mkdir -p "$HOME/bin"

    cat > "$WRAPPER_SCRIPT" << EOF
#!/bin/bash
cd "$CURRENT_DIR"
source venv/bin/activate
python main.py "\$@"
EOF

    chmod +x "$WRAPPER_SCRIPT"

    # Add to PATH if not already there
    if [[ ":$PATH:" != *":$HOME/bin:"* ]]; then
        echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
        print_success "Added $HOME/bin to PATH in ~/.bashrc"
        print_warning "Please run 'source ~/.bashrc' or restart your terminal"
    else
        print_success "PATH already includes $HOME/bin"
    fi
}

# Function to test installation
test_installation() {
    print_status "Testing installation..."

    # Test if command works
    if command_exists ai-cli; then
        print_success "AI CLI command is available"

        # Test help command
        if ai-cli --help >/dev/null 2>&1; then
            print_success "AI CLI is working correctly"
        else
            print_warning "AI CLI command found but may have issues"
        fi
    else
        print_warning "AI CLI command not found in PATH. You may need to restart your terminal or run 'source ~/.bashrc'"
    fi
}

# Function to show usage instructions
show_usage() {
    echo
    print_success "🎉 Installation completed!"
    echo
    echo "Usage instructions:"
    echo "  ai-cli                    # Start interactive chat"
    echo "  ai-cli --help            # Show help"
    echo "  ai-cli --read file.py    # Analyze a file"
    echo "  ai-cli --edit file.py    # Edit a file"
    echo "  ai-cli --system 'help'   # Get system help"
    echo
    echo "Configuration:"
    echo "  Edit .env file to customize settings"
    echo "  Default model can be set with DEFAULT_MODEL in .env"
    echo
    echo "Troubleshooting:"
    echo "  If 'ai-cli' command not found, run: source ~/.bashrc"
    echo "  Or restart your terminal"
    echo
}

# Main installation process
main() {
    echo "🤖 AI CLI Installation Script"
    echo "=============================="
    echo

    # Check prerequisites
    print_status "Checking prerequisites..."
    check_python || exit 1
    check_ollama || exit 1

    # Install AI CLI
    install_ai_cli

    # Setup configuration
    setup_config

    # Add to PATH
    add_to_path

    # Test installation
    test_installation

    # Show usage
    show_usage
}

# Run main function
main "$@"
