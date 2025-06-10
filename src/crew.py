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
    """Main crew class that orchestrates all agents intelligently"""
    
    def __init__(self):
        # Create all agents (but only use them when needed)
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
    
    def _analyze_user_input(self, user_input: str) -> dict:
        """Analyze user input to determine what agents are needed"""
        user_input_lower = user_input.lower().strip()
        
        analysis = {
            "needs_world": False,
            "needs_character": False,
            "needs_story": False,
            "action_type": "general",
            "can_handle_simple": False
        }
        
        # Movement actions
        if any(word in user_input_lower for word in ["go", "move", "walk", "travel", "north", "south", "east", "west"]):
            analysis["action_type"] = "movement"
            analysis["needs_world"] = True
            analysis["needs_story"] = True
            
        # Character interactions
        elif any(word in user_input_lower for word in ["talk", "speak", "say", "ask", "greet"]):
            analysis["action_type"] = "dialogue"
            analysis["needs_character"] = True
            analysis["needs_story"] = True
            
        # Exploration actions
        elif any(word in user_input_lower for word in ["look", "examine", "inspect", "search", "explore"]):
            analysis["action_type"] = "exploration" 
            if "around" in user_input_lower or "room" in user_input_lower:
                analysis["can_handle_simple"] = True  # Coordinator can handle this
            else:
                analysis["needs_world"] = True
                analysis["needs_story"] = True
            
        # Item interactions
        elif any(word in user_input_lower for word in ["take", "get", "pick", "grab", "use"]):
            analysis["action_type"] = "interaction"
            analysis["needs_world"] = True
            analysis["needs_story"] = True
            
        # Help/Info requests
        elif any(word in user_input_lower for word in ["help", "what", "where", "how", "who"]):
            analysis["action_type"] = "help"
            analysis["can_handle_simple"] = True  # Coordinator can handle this
            
        # General actions
        else:
            analysis["action_type"] = "general"
            analysis["needs_story"] = True
        
        return analysis
    
    def process_user_input(self, user_input: str) -> str:
        """Process user input through intelligent agent coordination"""
        
        try:
            # Step 1: Analyze what agents we need
            analysis = self._analyze_user_input(user_input)
            
            # Step 2: Handle simple requests directly with just the coordinator
            if analysis["can_handle_simple"]:
                print(f"📋 Handling simple request with Game Coordinator only...")
                
                coord_task = create_coordination_task(user_input)
                simple_crew = Crew(
                    agents=[self.game_coordinator],
                    tasks=[coord_task],
                    process=Process.sequential,
                    verbose=True
                )
                result = simple_crew.kickoff()
                return self._format_result(result)
            
            # Step 3: For complex requests, activate only necessary agents
            active_agents = [self.game_coordinator]  # Coordinator always involved
            active_tasks = [create_coordination_task(user_input)]
            
            print(f"📋 Analysis: {analysis['action_type']} action detected")
            
            # Add World Agent if needed
            if analysis["needs_world"]:
                print(f"🏗️  Activating World Agent...")
                active_agents.append(self.world_agent)
                world_request = self._generate_world_request(user_input, analysis)
                active_tasks.append(create_world_building_task(user_input, world_request))
            
            # Add Character Agent if needed  
            if analysis["needs_character"]:
                print(f"👥 Activating Character Agent...")
                active_agents.append(self.character_agent)
                char_request = self._generate_character_request(user_input, analysis)
                active_tasks.append(create_character_task(user_input, char_request))
            
            # Add Story Agent if needed
            if analysis["needs_story"]:
                print(f"📖 Activating Story Agent...")
                active_agents.append(self.story_agent)
                story_request = self._generate_story_request(user_input, analysis)
                active_tasks.append(create_story_task(user_input, story_request))
            
            print(f"🎯 Running {len(active_agents)} agents: {[agent.role for agent in active_agents]}")
            
            # Step 4: Execute only the necessary agents
            crew = Crew(
                agents=active_agents,
                tasks=active_tasks,
                process=Process.sequential,
                verbose=True
            )
            
            result = crew.kickoff()
            return self._format_result(result)
            
        except Exception as e:
            return f"An error occurred while processing your input: {str(e)}"
    
    def _generate_world_request(self, user_input: str, analysis: dict) -> str:
        """Generate specific request for World Agent based on analysis"""
        if analysis["action_type"] == "movement":
            return f"Handle player movement: {user_input}. Create new location if needed and move player there."
        elif analysis["action_type"] == "exploration":
            return f"Handle exploration request: {user_input}. Enhance current location or create new areas."
        elif analysis["action_type"] == "interaction":
            return f"Handle item interaction: {user_input}. Manage items and world objects."
        else:
            return f"Handle world aspects of: {user_input}"
    
    def _generate_character_request(self, user_input: str, analysis: dict) -> str:
        """Generate specific request for Character Agent based on analysis"""
        if analysis["action_type"] == "dialogue":
            return f"Handle character dialogue: {user_input}. Manage NPC interactions and conversations."
        else:
            return f"Handle character aspects of: {user_input}"
    
    def _generate_story_request(self, user_input: str, analysis: dict) -> str:
        """Generate specific request for Story Agent based on analysis"""
        return f"Handle narrative progression for: {user_input}. Create story events and meaningful choices."
    
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