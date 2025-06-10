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
    print("\nOur intelligent coordinator manages a crew of specialists:")
    print("🎯 Game Coordinator - Intelligently handles requests and delegates when needed")
    print("🏗️  World Builder - Creates detailed locations and environments") 
    print("👥 Character Manager - Manages NPCs and dialogue")
    print("📖 Story Director - Handles plot and choices")
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
    print("\n🎲 Your adventure is limited to 5 turns - make them count!")

def display_game_state():
    """Display current game state in a user-friendly format"""
    state = game_state.get_state()
    player = state["player"]
    turn_info = game_state.get_turn_info()
    
    print(f"\n📊 Player Status:")
    print(f"   Name: {player['name']}")
    print(f"   Location: {player['location'].replace('_', ' ').title()}")
    print(f"   Health: {player['health']}")
    print(f"   Items: {', '.join(player['inventory']) if player['inventory'] else 'None'}")
    print(f"   Turn: {turn_info['current_turn']}/{turn_info['max_turns']} ({turn_info['phase']} phase)")
    
    if turn_info['turns_remaining'] <= 1:
        print(f"   ⚠️  WARNING: Only {turn_info['turns_remaining']} turn(s) remaining!")

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

def generate_story_conclusion():
    """Generate a beautiful story conclusion and full adventure summary"""
    print("\n" + "="*80)
    print("🎭 GENERATING YOUR ADVENTURE EPILOGUE...")
    print("="*80)
    
    try:
        # Create Story Agent to generate the conclusion
        from agents.story_agent import create_story_director_agent, create_story_task
        from crewai import Crew, Process
        
        story_agent = create_story_director_agent()
        
        # Create conclusion task
        conclusion_task = create_story_task(
            "conclude adventure",
            """Create a beautiful, satisfying conclusion to this 5-turn adventure.
            
            Use the create_story_narrative tool to generate:
            1. A compelling epilogue that wraps up the story based on the player's choices and journey
            2. A complete narrative summary that shows how the story developed through player interactions
            3. Meaningful reflection on the adventure's themes and the player's decisions
            
            Make this feel like the conclusion of an epic tale that honors the player's journey."""
        )
        
        # Generate the conclusion
        conclusion_crew = Crew(
            agents=[story_agent],
            tasks=[conclusion_task],
            process=Process.sequential,
            verbose=False
        )
        
        conclusion_result = conclusion_crew.kickoff()
        
        # Display the beautiful conclusion
        print("\n🌟 YOUR ADVENTURE EPILOGUE:")
        print("="*80)
        print(conclusion_result)
        print("="*80)
        
        # Generate comprehensive adventure summary
        summary_task = create_story_task(
            "create comprehensive summary",
            """Create a detailed, engaging summary of the complete adventure showing:
            
            1. How the story began and the initial setting
            2. The key decisions the player made and their consequences  
            3. The locations explored and discoveries made
            4. How the narrative evolved based on player choices
            5. The dramatic conclusion and its meaning
            
            Write this as an engaging adventure recap that reads like an exciting story summary,
            highlighting the player's agency and the unique path their choices created."""
        )
        
        summary_crew = Crew(
            agents=[story_agent],
            tasks=[summary_task],
            process=Process.sequential,
            verbose=False
        )
        
        summary_result = summary_crew.kickoff()
        
        print("\n📚 YOUR COMPLETE ADVENTURE STORY:")
        print("="*80)
        print(summary_result)
        print("="*80)
        
    except Exception as e:
        print(f"❌ Error generating story conclusion: {e}")
        
        # Fallback: create a basic conclusion
        state = game_state.get_state()
        turn_info = game_state.get_turn_info()
        player_name = state["player"]["name"]
        
        print(f"\n🌟 YOUR ADVENTURE EPILOGUE:")
        print("="*80)
        print(f"As the adventure draws to a close, {player_name} reflects on the remarkable")
        print(f"journey that unfolded over {turn_info['current_turn']} meaningful turns.")
        print(f"Each choice shaped the path, each decision opened new possibilities.")
        print(f"This tale will be remembered as a unique adventure forged by courage,")
        print(f"curiosity, and the power of choice.")
        print("="*80)

def display_final_statistics():
    """Display comprehensive final statistics"""
    state = game_state.get_state()
    turn_info = game_state.get_turn_info()
    
    print(f"\n📊 ADVENTURE STATISTICS:")
    print("="*60)
    print(f"🎭 Hero: {state['player']['name']}")
    print(f"⏰ Turns Completed: {turn_info['current_turn']}/{turn_info['max_turns']}")
    print(f"🗺️  Locations Explored: {len(state['world']['locations'])}")
    print(f"👥 Characters Met: {len(state['characters'])}")
    print(f"📜 Story Events: {len(state['story']['events'])}")
    print(f"⚡ Choices Made: {len(state['story']['choices_made'])}")
    print(f"🏆 Adventure Phase Reached: {turn_info['phase'].title()}")
    
    # Show locations explored
    if state['world']['locations']:
        print(f"\n🗺️  Locations Discovered:")
        for location_name in state['world']['locations'].keys():
            print(f"   • {location_name.replace('_', ' ').title()}")
    
    # Show key choices made
    if state['story']['choices_made']:
        print(f"\n⚡ Key Decisions Made:")
        for i, choice in enumerate(state['story']['choices_made'][-5:], 1):  # Last 5 choices
            print(f"   {i}. {choice}")
    
    print("="*60)

def main():
    """Main game loop with rich final turn processing"""
    
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
            
            # Increment turn counter (except for special commands)
            game_state.increment_turn()
            turn_info = game_state.get_turn_info()
            
            print(f"\n🎲 Turn {turn_info['current_turn']}/{turn_info['max_turns']} ({turn_info['phase']} phase)")
            if turn_info['current_turn'] >= turn_info['max_turns']:
                print(f"🎭 FINAL TURN - Your epic conclusion awaits!")
            elif turn_info['turns_remaining'] <= 1:
                print(f"⚠️  Next turn will be your final turn!")
            elif turn_info['turns_remaining'] <= 2:
                print(f"⚠️  Only {turn_info['turns_remaining']} turns remaining!")
            
            # Process input through the intelligent coordinator system
            print("\n🎯 Coordinator processing your request...")
            print("-" * 50)
            
            response = fiction_crew.process_user_input(user_input)
            
            print("\n📜 Game Response:")
            print("=" * 50)
            print(response)
            print("=" * 50)
            
            # Show updated scene if location might have changed
            if any(word in user_input.lower() for word in ['go', 'move', 'travel', 'enter']):
                print("\n" + fiction_crew.get_current_scene_description())
            
            # Check if this was the final turn and now the game has ended
            if game_state.is_game_ended():
                print(f"\n🎊 ADVENTURE COMPLETE! 🎊")
                print("Your epic 5-turn journey has reached its magnificent conclusion...")
                
                # Generate beautiful story conclusion and summary
                generate_story_conclusion()
                
                # Display final statistics
                display_final_statistics()
                
                print(f"\n🙏 Thank you for playing, {player_name}!")
                print("Your unique adventure will be remembered forever.")
                print(f"📝 Complete session details saved to: {game_state.log_filename}")
                
                # Close logging and exit gracefully
                game_state.close_logging()
                break
            
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