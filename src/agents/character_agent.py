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
    """Create the Character Agent with enhanced tools for character continuity"""
    
    character_manager = Agent(
        role="Master Character Director & Dialogue Specialist",
        goal="Create engaging character interactions, maintain character consistency, and generate meaningful dialogue that advances the story",
        backstory="""You are a master character director who specializes in creating memorable NPCs 
        and handling player-character interactions. You excel at:
        
        CORE RESPONSIBILITIES:
        - Creating characters with distinct personalities and motivations
        - Generating realistic dialogue that advances the story
        - Maintaining character consistency across interactions
        - Ensuring characters respond logically to player choices
        - Managing character relationships and development
        
        CRITICAL: CHARACTER CONTINUITY (This fixes the Zephyr problem!)
        - When a character is introduced, they must remain present until logically removed
        - Characters should respond to direct questions and interactions
        - Never make characters disappear without explanation
        - Maintain personality consistency across all interactions
        - If a player asks a character a question, generate that character's response
        
        GAME_STATE INTEGRATION:
        - All character data is saved to and read from game_state
        - Character locations, relationships, and dialogue history are tracked
        - Coordinate with other agents through shared game_state knowledge
        
        DIALOGUE EXCELLENCE:
        - Generate natural, character-appropriate dialogue
        - Advance plot through character interactions
        - Provide information that helps player decision-making
        - Create emotional connections between player and NPCs
        
        TOOLS AVAILABLE:
        - get_character_context: See who's present and conversation history
        - handle_character_dialogue: Generate character responses to player input
        - create_character: Add new NPCs to the game world
        - move_character: Update character locations
        - update_character: Modify character traits or dialogue options
        - add_dialogue: Add specific dialogue options
        - get_characters: See all characters
        - get_characters_in_location: Find characters in specific places
        """,
        tools=[
            CreateCharacterTool(),
            GetCharactersTool(),
            AddDialogueTool(),
            GetCharactersInLocationTool(),
            HandleCharacterDialogueTool(),
            GetCharacterContextTool(),
            MoveCharacterTool(),
            UpdateCharacterTool()
        ],
        verbose=True,
        allow_delegation=False
    )
    
    return character_manager

def create_character_task(user_input: str, specific_request: str = None):
    """Create a task for the Character Agent with enhanced character interaction focus"""
    
    request = specific_request or f"Handle character aspects of: {user_input}"
    
    task = Task(
        description=f"""
        {request}
        
        CRITICAL: CHARACTER INTERACTION FOCUS
        - ALWAYS use get_character_context first to understand who is present and conversation history
        - If player is asking a character a question, use handle_character_dialogue to generate that character's response
        - If introducing new characters, use create_character tool to save them to game_state
        - If characters need to move, use move_character tool appropriately
        - NEVER make characters disappear randomly - maintain narrative continuity
        
        SPECIAL FOCUS FOR CHARACTER CONTINUITY:
        - If a character was previously introduced (like Zephyr), they should respond to player interactions
        - Generate appropriate dialogue that matches the character's personality
        - Ensure character responses advance the plot and provide useful information
        - Maintain the character's presence in the scene unless they logically leave
        
        CHARACTER INTERACTION WORKFLOW:
        1. Use get_character_context to see who's present and recent interactions
        2. If characters are present and player is interacting with them:
           - Use handle_character_dialogue to generate their response
           - Make the dialogue meaningful and character-appropriate
           - Advance the story through the character interaction
        3. If creating new characters, use create_character with full details
        4. Record important character developments with update_character
        
        Available tools for character management:
        - get_character_context: Get current character information and interaction history
        - handle_character_dialogue: Process character responses and save interactions
        - create_character: Add new characters to the game world  
        - move_character: Update character locations as needed
        - update_character: Modify character traits or add new dialogue options
        - add_dialogue: Add specific dialogue options to characters
        - get_characters: See all existing characters
        - get_characters_in_location: Find characters in specific locations
        
        GOAL: Create engaging, consistent character interactions that feel natural,
        advance the story, and maintain character presence. Never let characters 
        disappear without explanation - this is critical for narrative continuity!
        """,
        agent=create_character_manager_agent(),
        expected_output="Rich character interaction with appropriate dialogue, character development, and maintained character presence, all saved to game_state"
    )
    
    return task

class HandleCharacterDialogueTool(BaseTool):
    name: str = "handle_character_dialogue"
    description: str = "Generate dialogue response from a character to player interaction"
    
    def _run(self, dialogue_info: str) -> str:
        """Handle character dialogue and save important interactions to game_state"""
        try:
            # Parse dialogue request
            if isinstance(dialogue_info, str):
                try:
                    data = json.loads(dialogue_info)
                except json.JSONDecodeError:
                    # Simple format: "character_name: player_said_this"
                    if ":" in dialogue_info:
                        parts = dialogue_info.split(":", 1)
                        character_name = parts[0].strip()
                        player_input = parts[1].strip()
                    else:
                        return "❌ Error: Use format 'character_name: what_player_said'"
                    data = {"character": character_name, "player_input": player_input}
            else:
                data = dialogue_info
            
            character_name = data.get("character")
            player_input = data.get("player_input", "")
            topic = data.get("topic", "general")
            
            # Record the interaction in game_state
            game_state.add_story_event(f"Player spoke with {character_name}: {player_input}")
            
            # Get character info for context
            characters = game_state.get_state()["characters"]
            if character_name in characters:
                char_data = characters[character_name]
                personality = char_data.get("personality", "friendly")
                description = char_data.get("description", "")
                
                return f"✅ {character_name} (personality: {personality}) responds to '{player_input}' about {topic} - interaction saved to game_state"
            else:
                return f"❌ Character {character_name} not found in game_state"
            
        except Exception as e:
            return f"❌ Error handling dialogue: {str(e)}"

class GetCharacterContextTool(BaseTool):
    name: str = "get_character_context"
    description: str = "Get information about characters in the current scene and recent interactions"
    
    def _run(self) -> str:
        """Get character context from game_state"""
        state = game_state.get_state()
        current_location = state["player"]["location"]
        
        # Find characters in current location
        characters_here = {}
        for char_name, char_data in state["characters"].items():
            if char_data.get("location") == current_location:
                characters_here[char_name] = {
                    "name": char_name,
                    "description": char_data.get("description", ""),
                    "personality": char_data.get("personality", ""),
                    "dialogue_options": char_data.get("dialogue_options", {})
                }
        
        # Get recent story events that mention characters
        recent_events = []
        for event in state["story"]["events"][-10:]:  # Last 10 events
            if any(char_name.lower() in event.lower() for char_name in characters_here.keys()):
                recent_events.append(event)
        
        context = {
            "current_location": current_location,
            "characters_present": characters_here,
            "recent_character_events": recent_events,
            "player_choices": state["story"]["choices_made"][-3:],  # Last 3 choices
            "turn_info": game_state.get_turn_info()
        }
        
        return json.dumps(context, indent=2)

class MoveCharacterTool(BaseTool):
    name: str = "move_character"
    description: str = "Move a character to a different location"
    
    def _run(self, move_info: str) -> str:
        """Move character to new location in game_state"""
        try:
            if isinstance(move_info, str):
                try:
                    data = json.loads(move_info)
                except json.JSONDecodeError:
                    if ":" in move_info:
                        parts = move_info.split(":", 1)
                        character_name = parts[0].strip()
                        new_location = parts[1].strip()
                    else:
                        return "❌ Error: Use format 'character_name: new_location'"
                    data = {"character": character_name, "location": new_location}
            else:
                data = move_info
            
            character_name = data.get("character")
            new_location = data.get("location")
            
            # Update character location in game_state
            state = game_state.get_state()
            if character_name in state["characters"]:
                old_location = state["characters"][character_name].get("location", "unknown")
                state["characters"][character_name]["location"] = new_location
                game_state.log_event(f"Character {character_name} moved from {old_location} to {new_location}")
                return f"✅ Moved {character_name} to {new_location} in game_state"
            else:
                return f"❌ Character {character_name} not found in game_state"
                
        except Exception as e:
            return f"❌ Error moving character: {str(e)}"

class UpdateCharacterTool(BaseTool):
    name: str = "update_character"
    description: str = "Update character information like personality, description, or dialogue options"
    
    def _run(self, update_info: str) -> str:
        """Update character information in game_state"""
        try:
            if isinstance(update_info, str):
                try:
                    data = json.loads(update_info)
                except json.JSONDecodeError:
                    return "❌ Error: update_info must be JSON format like {\"character\": \"name\", \"field\": \"personality\", \"value\": \"new_value\"}"
            else:
                data = update_info
            
            character_name = data.get("character")
            field = data.get("field")
            value = data.get("value")
            
            # Update character in game_state
            state = game_state.get_state()
            if character_name in state["characters"]:
                state["characters"][character_name][field] = value
                game_state.log_event(f"Updated {character_name}'s {field}")
                return f"✅ Updated {character_name}'s {field} in game_state"
            else:
                return f"❌ Character {character_name} not found in game_state"
                
        except Exception as e:
            return f"❌ Error updating character: {str(e)}"