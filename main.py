#!/usr/bin/env python3
"""
AI Assistant CLI - Like Google Gemini for your terminal
Main entry point for the application
"""
import argparse
from rich.console import Console

from ai_cli.assistant import AIAssistant

console = Console()


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="AI Assistant CLI - Like Google Gemini for your terminal",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
    Examples:
    %(prog)s                                    # Start interactive chat
    %(prog)s --read file.py                     # Analyze a file
    %(prog)s --read file.py --prompt "explain"  # Analyze with custom prompt
    %(prog)s --edit file.py "add comments"      # Edit a file
    %(prog)s --system "how to install docker"   # Ask about system
        """,
    )

    parser.add_argument("--model", "-m", help="Specify model to use")
    parser.add_argument("--read", "-r", metavar="FILE", help="Read and analyze a file")
    parser.add_argument(
        "--edit", "-e", metavar="FILE", help="Edit a file with AI assistance"
    )
    parser.add_argument("--prompt", "-p", help="Custom prompt for file analysis")
    parser.add_argument("--instruction", "-i", help="Instruction for file editing")
    parser.add_argument("--system", "-s", help="Ask about system/Ubuntu")
    parser.add_argument(
        "--chat", "-c", action="store_true", help="Start interactive chat (default)"
    )

    return parser.parse_args()


def main():
    """Main application entry point"""
    args = parse_arguments()

    # Create assistant
    assistant = AIAssistant(args.model)

    try:
        if args.read:
            assistant.analyze_file(args.read, args.prompt)
        elif args.edit:
            instruction = args.instruction or console.input(
                "[bold yellow]Enter editing instruction:[/bold yellow] "
            )
            assistant.edit_file(args.edit, instruction)
        elif args.system:
            assistant.system_assistant(args.system)
        else:
            # Default to chat mode
            assistant.chat_mode()

    except KeyboardInterrupt:
        console.print("\n[bold magenta]Goodbye![/bold magenta]")


if __name__ == "__main__":
    main()
