from crewai import Agent, Task
from crewai.tools import BaseTool
import json
from game_state import game_state

class CreateCharacterTool(BaseTool):
    name: str = "create_character"
    description: str = "Create a new NPC character in the game world"
    
    def _run(self, character_info: str) -> str:
        """Create a new character/NPC in the game."""
        try:
            # Handle both JSON and simple string input
            if isinstance(character_info, str):
                try:
                    character_data = json.loads(character_info)
                except json.JSONDecodeError:
                    # If not JSON, return error with format help
                    return "Error: character_info must be JSON format like {\"name\": \"character_name\", \"location\": \"place\", \"personality\": \"trait\", \"description\": \"character description\"}"
            else:
                character_data = character_info
                
            character_name = character_data.get("name")
            if not character_name:
                return "Error: character must have a name"
                
            game_state.add_character(character_name, character_data)
            return f"Successfully created character: {character_name}"
        except Exception as e:
            return f"Error creating character: {str(e)}"

class GetCharactersTool(BaseTool):
    name: str = "get_characters"
    description: str = "Get all characters currently in the game"
    
    def _run(self) -> str:
        """Get all characters in the game"""
        characters = game_state.get_state()["characters"]
        return json.dumps(characters, indent=2)

class AddDialogueTool(BaseTool):
    name: str = "add_dialogue"
    description: str = "Add dialogue options to an existing character"
    
    def _run(self, dialogue_info: str) -> str:
        """Add dialogue options to a character."""
        try:
            # Handle both JSON and simple string input
            if isinstance(dialogue_info, str):
                try:
                    data = json.loads(dialogue_info)
                except json.JSONDecodeError:
                    # If not JSON, return error with format help
                    return "Error: dialogue_info must be JSON format like {\"character\": \"name\", \"dialogue\": \"text\", \"response_to\": \"situation\"}"
            else:
                data = dialogue_info
                
            character_name = data.get("character")
            dialogue = data.get("dialogue")
            response_to = data.get("response_to", "general")
            
            characters = game_state.get_state()["characters"]
            if character_name in characters:
                if "dialogue_options" not in characters[character_name]:
                    characters[character_name]["dialogue_options"] = {}
                characters[character_name]["dialogue_options"][response_to] = dialogue
                game_state.log_event(f"Added dialogue to {character_name}")
                return f"Added dialogue to {character_name}"
            else:
                return f"Character {character_name} does not exist"
        except Exception as e:
            return f"Error adding dialogue: {str(e)}"

class GetCharactersInLocationTool(BaseTool):
    name: str = "get_characters_in_location"
    description: str = "Get all characters present in a specific location"
    
    def _run(self, location: str) -> str:
        """Get characters present in a specific location"""
        characters = game_state.get_state()["characters"]
        chars_in_location = []
        
        for char_name, char_data in characters.items():
            if char_data.get("location") == location:
                chars_in_location.append({
                    "name": char_name,
                    "description": char_data.get("description", ""),
                    "personality": char_data.get("personality", "")
                })
        
        return json.dumps(chars_in_location, indent=2)

def create_character_manager_agent():
    """Create the Character Agent with tools"""
    
    character_manager = Agent(
        role="Character Agent",
        goal="Create memorable NPCs and manage character interactions and dialogue",
        backstory="""You are a skilled character designer who creates compelling NPCs with 
        distinct personalities, interesting backstories, and engaging dialogue. You understand 
        how characters drive narrative and create meaningful interactions for players.
        You have tools to create characters, manage dialogue, and track character locations.""",
        tools=[
            CreateCharacterTool(),
            GetCharactersTool(),
            AddDialogueTool(),
            GetCharactersInLocationTool()
        ],
        verbose=True,
        allow_delegation=False
    )
    
    return character_manager

def create_character_task(user_input: str, specific_request: str = None):
    """Create a task for the Character Agent"""
    
    request = specific_request or f"Handle character aspects of: {user_input}"
    
    task = Task(
        description=f"""
        {request}
        
        You have access to these tools:
        - create_character: Create new NPCs with JSON format
        - get_characters: See all existing characters
        - add_dialogue: Add dialogue options to characters
        - get_characters_in_location: Find characters in specific locations
        
        Use your tools to create engaging character interactions and memorable NPCs.
        """,
        agent=create_character_manager_agent(),
        expected_output="Description of character interactions and any new NPCs created"
    )
    
    return task