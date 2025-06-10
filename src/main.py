#!/usr/bin/env python3
"""
Interactive Fiction Engine - Main Game Loop
A multi-agent system for creating interactive fiction experiences
"""

import os
import sys
from dotenv import load_dotenv
from crew import fiction_crew
from game_state import game_state

def display_welcome():
    """Display welcome message and game instructions"""
    print("\n" + "="*60)
    print("🎮 INTERACTIVE FICTION ENGINE 🎮")
    print("A Multi-Agent Storytelling Experience")
    print("="*60)
    print("\nWelcome to an interactive fiction adventure powered by AI agents!")
    print("\nOur crew of specialized agents will create your story:")
    print("🏗️  World Builder - Creates locations and environments")
    print("👥 Character Manager - Manages NPCs and dialogue")
    print("📖 Story Director - Handles plot and choices")
    print("🎯 Game Coordinator - Orchestrates everything")
    print("\n" + "-"*60)
    print("\nCommands you can try:")
    print("• 'look around' - examine your surroundings")
    print("• 'go [direction]' - move to another location")
    print("• 'talk to [character]' - interact with NPCs")
    print("• 'take [item]' - pick up items")
    print("• 'summarize' - get AI story summary")
    print("• 'status' - check your current status")
    print("• 'help' - get assistance")
    print("• 'quit' - exit the game")
    print("-"*60)

def display_game_state():
    """Display current game state in a user-friendly format"""
    state = game_state.get_state()
    player = state["player"]
    
    print(f"\n📊 Player Status:")
    print(f"   Name: {player['name']}")
    print(f"   Location: {player['location'].replace('_', ' ').title()}")
    print(f"   Health: {player['health']}")
    print(f"   Items: {', '.join(player['inventory']) if player['inventory'] else 'None'}")

def initialize_player():
    """Initialize player information"""
    print("\n🌟 Let's begin your adventure!")
    player_name = input("What is your name, adventurer? ").strip()
    
    if not player_name:
        player_name = "Mysterious Traveler"
    
    # Update game state with player name
    game_state.update_player({"name": player_name})
    
    print(f"\nWelcome, {player_name}! Your adventure begins now...")
    return player_name

def main():
    """Main game loop"""
    
    # Load environment variables
    load_dotenv()
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in environment variables.")
        print("Please create a .env file with your OpenAI API key.")
        print("Example: OPENAI_API_KEY=your_api_key_here")
        return
    
    # Display welcome message
    display_welcome()
    
    # Initialize player
    player_name = initialize_player()
    
    # Show initial scene
    print(fiction_crew.get_current_scene_description())
    
    # Main game loop
    while True:
        try:
            # Get user input
            print("\n" + ">"*40)
            user_input = input("What would you like to do? ").strip()
            
            # Handle special commands
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print(f"\n👋 Thanks for playing, {player_name}! Your adventure will be remembered.")
                game_state.close_logging()
                break
                
            elif user_input.lower() in ['status', 'stats']:
                display_game_state()
                continue
                
            elif user_input.lower() in ['summarize', 'summary', 'story']:
                print("\n📚 Generating story summary with AI...")
                print("-" * 50)
                
                # Create a specific task for story summarization
                from agents.story_agent import create_story_director_agent, create_story_task
                summary_agent = create_story_director_agent()
                summary_task = create_story_task(
                    "summarize story", 
                    "Use create_story_narrative tool to generate a compelling narrative summary of the adventure so far"
                )
                
                from crewai import Crew, Process
                summary_crew = Crew(
                    agents=[summary_agent],
                    tasks=[summary_task],
                    process=Process.sequential,
                    verbose=False
                )
                
                try:
                    summary_result = summary_crew.kickoff()
                    print("\n📖 YOUR ADVENTURE SO FAR:")
                    print("=" * 60)
                    print(summary_result)
                    print("=" * 60)
                except Exception as e:
                    print(f"❌ Error generating summary: {e}")
                    
                continue
                
            elif user_input.lower() in ['scene', 'look', 'look around']:
                print(fiction_crew.get_current_scene_description())
                continue
                
            elif user_input.lower() in ['help', '?']:
                print("\n🤔 Need help? Try commands like:")
                print("  • 'go north' - move to another area")
                print("  • 'examine room' - look around carefully")
                print("  • 'talk to wizard' - speak with characters")
                print("  • 'take sword' - pick up items")
                print("  • 'summarize' - get AI story summary")
                print("  • 'status' - check your current state")
                continue
            
            elif not user_input:
                print("Please enter a command. Type 'help' for assistance.")
                continue
            
            # Process input through the intelligent agent system
            print("\n🤖 Analyzing your request...")
            print("-" * 50)
            
            response = fiction_crew.process_user_input(user_input)
            
            print("\n📜 Game Response:")
            print("=" * 50)
            print(response)
            print("=" * 50)
            
            # Show updated scene if location might have changed
            if any(word in user_input.lower() for word in ['go', 'move', 'travel', 'enter']):
                print("\n" + fiction_crew.get_current_scene_description())
            
        except KeyboardInterrupt:
            print(f"\n\n👋 Game interrupted. Thanks for playing, {player_name}!")
            game_state.close_logging()
            break
            
        except Exception as e:
            print(f"\n❌ An error occurred: {str(e)}")
            print("Please try a different command or type 'help' for assistance.")
    
    # Close logging when game ends
    game_state.close_logging()

if __name__ == "__main__":
    main()