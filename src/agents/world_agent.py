from crewai import Agent, Task
from crewai.tools import BaseTool
import json
from game_state import game_state

class CreateLocationTool(BaseTool):
    name: str = "create_location"
    description: str = "Create a new location in the game world. Pass JSON string with name, description, exits, and items"
    
    def _run(self, location_info: str) -> str:
        """Create a new location in the game world."""
        try:
            # Handle both string and already-parsed JSON
            if isinstance(location_info, str):
                # If it's a string, try to parse it as JSON
                try:
                    location_data = json.loads(location_info)
                except json.JSONDecodeError:
                    # If JSON parsing fails, treat as simple description
                    # Extract name from the beginning if it follows "name: description" format
                    if ":" in location_info:
                        parts = location_info.split(":", 1)
                        location_name = parts[0].strip()
                        description = parts[1].strip()
                    else:
                        location_name = "new_location"
                        description = location_info
                    
                    location_data = {
                        "name": location_name,
                        "description": description,
                        "exits": ["west"],  # Default back to starting area
                        "items": []
                    }
            else:
                location_data = location_info
                
            location_name = location_data.get("name", "unnamed_location")
            game_state.add_location(location_name, location_data)
            return f"Successfully created location: {location_name}"
        except Exception as e:
            return f"Error creating location: {str(e)}"

class GetWorldStateTool(BaseTool):
    name: str = "get_world_state"
    description: str = "Get the current state of the game world including all locations"
    
    def _run(self) -> str:
        """Get current world state for context"""
        world_info = game_state.get_state()["world"]
        return json.dumps(world_info, indent=2)

class AddItemToLocationTool(BaseTool):
    name: str = "add_item_to_location"
    description: str = "Add an item to a specific location in the game world"
    
    def _run(self, item_info: str) -> str:
        """Add an item to a specific location."""
        try:
            # Handle both JSON and simple string input
            if isinstance(item_info, str):
                try:
                    data = json.loads(item_info)
                except json.JSONDecodeError:
                    # If not JSON, return error message
                    return "Error: item_info must be JSON format like {\"location\": \"place\", \"item\": \"item_name\", \"description\": \"item description\"}"
            else:
                data = item_info
                
            location_name = data.get("location")
            item = data.get("item")
            description = data.get("description", "")
            
            locations = game_state.get_state()["world"]["locations"]
            if location_name in locations:
                if "items" not in locations[location_name]:
                    locations[location_name]["items"] = []
                locations[location_name]["items"].append({
                    "name": item,
                    "description": description
                })
                game_state.log_event(f"Added item {item} to {location_name}")
                return f"Added {item} to {location_name}"
            else:
                return f"Location {location_name} does not exist"
        except Exception as e:
            return f"Error adding item: {str(e)}"

class MovePlayerTool(BaseTool):
    name: str = "move_player"
    description: str = "Move the player to a new location"
    
    def _run(self, location_name: str) -> str:
        """Move player to a new location."""
        try:
            game_state.set_current_location(location_name)
            return f"Player moved to: {location_name}"
        except Exception as e:
            return f"Error moving player: {str(e)}"

def create_world_builder_agent():
    """Create the World Agent with tools"""
    
    world_builder = Agent(
        role="World Agent",
        goal="Create immersive locations and manage the game world environment",
        backstory="""You are a master world builder who creates rich, detailed environments 
        for interactive fiction. You design locations with vivid descriptions, logical connections, 
        and interesting items that enhance the player's experience. You have tools to create locations,
        manage world state, add items, and move players between locations.""",
        tools=[
            CreateLocationTool(),
            GetWorldStateTool(),
            AddItemToLocationTool(),
            MovePlayerTool()
        ],
        verbose=True,
        allow_delegation=False
    )
    
    return world_builder

def create_world_building_task(user_input: str, specific_request: str = None):
    """Create a task for the World Agent"""
    
    request = specific_request or f"Handle world-building aspects of: {user_input}"
    
    task = Task(
        description=f"""
        {request}
        
        You have access to these tools:
        - create_location: Create new locations with JSON format
        - get_world_state: Check current world state
        - add_item_to_location: Add items to locations
        - move_player: Move player to new location
        
        Use your tools wisely to create engaging world experiences.
        When creating locations, use proper JSON format with name, description, exits, and items.
        """,
        agent=create_world_builder_agent(),
        expected_output="Confirmation of world changes made and description of the new environment"
    )
    
    return task