#!/usr/bin/env python3
"""
Interactive Fiction Engine - Main Entry Point
A multi-agent storytelling system using CrewAI

Team Members:
- Member 1: World Agent (Environmental Designer)
- Member 2: Character Agent (Character Creator)  
- Member 3: Story Agent (Narrative Director)
- Member 4: Coordinator Agent (Game Master)
"""

import os
import sys
from colorama import init, Fore, Style
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Initialize colorama for cross-platform color support
init()

# Initialize rich console
console = Console()

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from crew import InteractiveFictionCrew, display_scene, get_player_input, display_help
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)


def show_welcome_banner():
    """Display welcome banner"""
    banner = Text()
    banner.append("🎭 Interactive Fiction Engine\n", style="bold blue")
    banner.append("Powered by CrewAI Multi-Agent System\n\n", style="blue")
    banner.append("✨ Four AI agents working together to create your story:\n", style="green")
    banner.append("🌍 World Agent - Creates immersive environments\n", style="cyan")
    banner.append("👥 Character Agent - Brings NPCs to life\n", style="yellow") 
    banner.append("📖 Story Agent - Weaves compelling narratives\n", style="magenta")
    banner.append("🎯 Coordinator Agent - Orchestrates the experience\n", style="red")
    
    console.print(Panel(banner, title="Welcome", border_style="bright_green"))


def check_api_key():
    """Check if OpenAI API key is configured"""
    if not os.getenv("OPENAI_API_KEY"):
        console.print(Panel(
            "❌ OpenAI API Key not found!\n\n"
            "Please set your API key in the .env file:\n"
            "OPENAI_API_KEY=your_key_here\n\n"
            "You can get an API key from: https://platform.openai.com/api-keys",
            title="Configuration Error",
            border_style="red"
        ))
        return False
    return True


def main():
    """Main game loop"""
    # Show welcome banner
    show_welcome_banner()
    
    # Check API configuration
    if not check_api_key():
        return
    
    try:
        console.print("🚀 Initializing AI agents...", style="yellow")
        
        # Initialize the crew with better error handling
        crew = InteractiveFictionCrew(
            model_name="gpt-3.5-turbo",  # More affordable option
            temperature=0.8  # Higher creativity for storytelling
        )
        
        console.print("✅ All agents ready!", style="green")
        console.print("\n💡 Type 'help' at any time for commands\n", style="blue")
        
        # Start a new story
        console.print("🎬 Starting your adventure...", style="yellow")
        opening_scene = crew.start_new_story()
        
        # Display the opening scene
        console.print(Panel(opening_scene, title="📖 Your Story Begins", border_style="blue"))
        
        # Game loop
        turn_count = 0
        while True:
            turn_count += 1
            
            # Get player input
            user_input = get_player_input(f"\n🎮 Turn {turn_count} - What do you choose? ")
            
            # Handle special commands
            if user_input.lower() in ["quit", "exit", "q"]:
                console.print("👋 Thanks for playing! Your story will be remembered...", style="green")
                break
                
            elif user_input.lower() in ["help", "h"]:
                display_help()
                turn_count -= 1  # Don't count help as a turn
                continue
                
            elif user_input.lower() in ["status", "stats"]:
                status = crew.get_story_status()
                status_text = (f"📊 Game Status:\n"
                             f"Turn: {status['turn']}\n"
                             f"Choices Made: {status['choices_made']}\n"
                             f"Story Length: {status['story_length']} events")
                console.print(Panel(status_text, title="Status", border_style="cyan"))
                turn_count -= 1
                continue
                
            elif user_input.lower() in ["summary", "recap"]:
                console.print("📝 Generating story summary...", style="yellow")
                summary = crew.get_story_summary()
                console.print(Panel(summary, title="Story So Far", border_style="magenta"))
                turn_count -= 1
                continue
                
            elif user_input.lower() in ["save"]:
                filename = f"story_save_turn_{turn_count}.json"
                if crew.save_story(filename):
                    console.print(f"💾 Game saved as {filename}", style="green")
                else:
                    console.print("❌ Failed to save game", style="red")
                turn_count -= 1
                continue
            
            # Process the player's choice
            try:
                console.print("⚙️ AI agents are crafting your next scene...", style="yellow")
                next_scene = crew.process_choice(user_input)
                
                # Display the next scene
                console.print(Panel(
                    next_scene, 
                    title=f"📖 Turn {turn_count} Result", 
                    border_style="blue"
                ))
                
            except Exception as e:
                console.print(f"❌ Error processing choice: {e}", style="red")
                console.print("🔄 Try rephrasing your choice or type 'help' for guidance", style="yellow")
                turn_count -= 1  # Don't count errors as turns
                
    except KeyboardInterrupt:
        console.print("\n👋 Game interrupted. Thanks for playing!", style="yellow")
        
    except Exception as e:
        console.print(f"❌ Unexpected error: {e}", style="red")
        console.print("Please check your internet connection and API key.", style="yellow")


def run_demo():
    """Run a quick demo of the system"""
    console.print("🧪 Running Interactive Fiction Engine Demo", style="bold blue")
    
    if not check_api_key():
        return
        
    try:
        crew = InteractiveFictionCrew()
        
        # Demo: Create a fantasy opening
        console.print("Creating a fantasy adventure opening...", style="yellow")
        opening = crew.start_new_story("fantasy_adventure")
        console.print(Panel(opening, title="Demo Opening", border_style="green"))
        
        # Demo: Process a sample choice
        console.print("Processing sample choice: 'I approach the mysterious door carefully'", style="yellow")
        result = crew.process_choice("I approach the mysterious door carefully")
        console.print(Panel(result, title="Demo Result", border_style="green"))
        
        console.print("✅ Demo completed successfully!", style="green")
        
    except Exception as e:
        console.print(f"❌ Demo failed: {e}", style="red")


if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        run_demo()
    else:
        main()