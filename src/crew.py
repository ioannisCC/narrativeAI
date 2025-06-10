from crewai import Crew, Process
from agents.world_agent import create_world_builder_agent, create_world_building_task
from agents.character_agent import create_character_manager_agent, create_character_task
from agents.story_agent import create_story_director_agent, create_story_task
from agents.coordinator_agent import create_game_coordinator_agent, create_coordination_task
from game_state import game_state
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class InteractiveFictionCrew:
    """Main crew class that orchestrates intelligent agent coordination"""
    
    def __init__(self):
        # Create all agents (available for delegation when needed)
        self.coordinator_agent = create_game_coordinator_agent()
        self.world_agent = create_world_builder_agent()
        self.character_agent = create_character_manager_agent()
        self.story_agent = create_story_director_agent()
        
        # Initialize the game with starting content
        self._initialize_starting_world()
    
    def _initialize_starting_world(self):
        """Initialize the game with some starting content"""
        # Create initial location
        starting_location = {
            "name": "starting_room",
            "description": "You find yourself in a mysterious forest clearing. Ancient trees tower around you, and shafts of golden sunlight filter through the canopy. There's a sense of magic in the air.",
            "exits": ["north", "east", "west"],
            "items": [
                {"name": "old_map", "description": "A weathered map showing nearby locations"},
                {"name": "wooden_staff", "description": "A simple wooden staff that seems to hum with energy"}
            ]
        }
        
        game_state.add_location("starting_room", starting_location)
        
        # Add initial story event
        game_state.add_story_event("The adventure begins in a mysterious forest clearing")
    
    def process_user_input(self, user_input: str) -> str:
        """Process user input through ONLY the coordinator agent"""
        
        try:
            print(f"🤖 Processing with coordinator agent...")
            
            # ALWAYS use ONLY the coordinator agent - no analysis, no multiple agents
            coord_task = create_coordination_task(user_input)
            
            # Single-agent crew ONLY
            crew = Crew(
                agents=[self.coordinator_agent],  # ONLY coordinator
                tasks=[coord_task],
                process=Process.sequential,
                verbose=False  # Turn off verbose for speed
            )
            
            result = crew.kickoff()
            return self._format_result(result)
            
        except Exception as e:
            return f"An error occurred while processing your input: {str(e)}"
    
    def _format_result(self, result) -> str:
        """Format the crew result into a readable string"""
        if hasattr(result, 'raw'):
            return str(result.raw)
        else:
            return str(result)
    
    def get_game_status(self) -> dict:
        """Get current game status"""
        return game_state.get_state()
    
    def get_current_scene_description(self) -> str:
        """Get a formatted description of the current scene"""
        state = game_state.get_state()
        current_location = state["player"]["location"]
        location_info = state["world"]["locations"].get(current_location, {})
        
        description = f"\n--- {current_location.replace('_', ' ').title()} ---\n"
        description += location_info.get("description", "You are in an unknown place") + "\n"
        
        # Add items
        items = location_info.get("items", [])
        if items:
            description += "\nItems here:\n"
            for item in items:
                if isinstance(item, dict):
                    description += f"  - {item['name']}: {item.get('description', '')}\n"
                else:
                    description += f"  - {item}\n"
        
        # Add exits
        exits = location_info.get("exits", [])
        if exits:
            description += f"\nExits: {', '.join(exits)}\n"
        
        # Add characters
        characters_here = []
        for char_name, char_data in state["characters"].items():
            if char_data.get("location") == current_location:
                characters_here.append(char_name)
        
        if characters_here:
            description += f"\nCharacters here: {', '.join(characters_here)}\n"
        
        return description

# Create global crew instance
fiction_crew = InteractiveFictionCrew()