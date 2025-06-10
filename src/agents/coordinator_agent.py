from crewai import Agent, Task
from crewai.tools import BaseTool
import json
from game_state import game_state

class GetFullGameStateTool(BaseTool):
    name: str = "get_full_game_state"
    description: str = "Get the complete current game state for coordination"
    
    def _run(self) -> str:
        """Get the complete current game state"""
        return game_state.to_json()

class GetCurrentSceneTool(BaseTool):
    name: str = "get_current_scene"
    description: str = "Get detailed description of the current game scene"
    
    def _run(self) -> str:
        """Get description of current game scene"""
        state = game_state.get_state()
        current_location = state["player"]["location"]
        location_info = state["world"]["locations"].get(current_location, {})
        
        # Get characters in current location
        characters_here = []
        for char_name, char_data in state["characters"].items():
            if char_data.get("location") == current_location:
                characters_here.append(char_name)
        
        scene = {
            "location": current_location,
            "description": location_info.get("description", "You are in an unknown place"),
            "items": location_info.get("items", []),
            "exits": location_info.get("exits", []),
            "characters": characters_here,
            "player_stats": state["player"]
        }
        
        return json.dumps(scene, indent=2)

class LogGameEventTool(BaseTool):
    name: str = "log_game_event"
    description: str = "Log important game events for tracking"
    
    def _run(self, event: str) -> str:
        """Log an important game event"""
        game_state.log_event(event)
        return f"Logged: {event}"

class UpdatePlayerLocationTool(BaseTool):
    name: str = "update_player_location"
    description: str = "Move the player to a new location"
    
    def _run(self, location_name: str) -> str:
        """Move player to a new location"""
        try:
            game_state.set_current_location(location_name)
            return f"Player moved to: {location_name}"
        except Exception as e:
            return f"Error moving player: {str(e)}"

class CreateBasicLocationTool(BaseTool):
    name: str = "create_basic_location"
    description: str = "Create a simple location if it doesn't exist"
    
    def _run(self, location_info: str) -> str:
        """Create a basic location"""
        try:
            # Handle JSON string input
            if isinstance(location_info, str):
                try:
                    data = json.loads(location_info)
                except json.JSONDecodeError:
                    # Simple name: description format
                    if ":" in location_info:
                        parts = location_info.split(":", 1)
                        name = parts[0].strip()
                        description = parts[1].strip()
                    else:
                        name = location_info.strip()
                        description = f"A new area of the forest."
                    
                    data = {
                        "name": name,
                        "description": description,
                        "exits": ["back"],
                        "items": []
                    }
            else:
                data = location_info
            
            location_name = data.get("name")
            game_state.add_location(location_name, data)
            return f"Created location: {location_name}"
        except Exception as e:
            return f"Error creating location: {str(e)}"

def create_game_coordinator_agent():
    """Create the Coordinator Agent with basic tools"""
    
    game_coordinator = Agent(
        role="Coordinator Agent",
        goal="Handle user requests intelligently, honor player choices, and delegate only when necessary",
        backstory="""You are the master game coordinator who ensures player choices are ALWAYS honored.
        
        CRITICAL RULES:
        1. ALWAYS respect and follow through on player choices - never ignore them
        2. When players choose numbered options, record their choice and follow that path
        3. Use simple tool inputs - pass plain text strings, never JSON objects
        4. Only delegate to specialists for complex tasks like detailed NPCs or elaborate story events
        
        You have access to game context, player state, location data, story progression, and turn information.
        Always provide rich, immersive responses that honor what the player chose to do.""",
        tools=[
            GetFullGameStateTool(),
            GetCurrentSceneTool(),
            LogGameEventTool(),
            UpdatePlayerLocationTool(),
            CreateBasicLocationTool()
        ],
        verbose=True,
        allow_delegation=True
    )
    
    return game_coordinator

def create_coordination_task(user_input: str):
    """Create a smart coordination task that lets the LLM decide what to do"""
    
    # Get turn information for context
    turn_info = game_state.get_turn_info()
    turn_context = ""
    
    if turn_info['current_turn'] > 0:
        turn_context = f"""
        
        TURN PROGRESSION AWARENESS:
        • Current Turn: {turn_info['current_turn']}/{turn_info['max_turns']} 
        • Phase: {turn_info['phase']} 
        • Turns Remaining: {turn_info['turns_remaining']}
        • {"⚠️  FINAL TURN - Must conclude the adventure!" if turn_info['turns_remaining'] <= 1 else ""}
        
        PACING GUIDANCE:
        - Beginning phase (1-1): World-building, discovery, setup
        - Middle phase (2-3): Challenges, character development, complications  
        - Late phase (4): Build toward climax, increase stakes
        - Climax phase (5): Epic conclusion, resolve all plot threads
        
        Adjust your response and any delegated tasks to match the current story phase.
        """
    
    task = Task(
        description=f"""
        INTELLIGENT COORDINATION TASK
        User Input: "{user_input}"
        {turn_context}
        
        Your job is to handle this request efficiently using your understanding of the game context.
        
        AVAILABLE TOOLS:
        • get_full_game_state - See complete game state including player, locations, characters, story
        • get_current_scene - Get detailed current location and scene information  
        • log_game_event - Record important events
        • update_player_location - Move player to new location
        • create_basic_location - Create simple locations as needed
        
        DECISION PROCESS:
        1. Use get_current_scene and/or get_full_game_state to understand the current context
        2. Consider the turn progression when crafting responses and making decisions
        3. Decide if you can handle this request directly:
           - Simple movement (north, south, east, west) → Use your tools to move player and describe
           - Basic exploration (look around) → Use current scene to provide rich description
           - Status/help requests → Use game state to provide information
        4. OR if you need specialist expertise, delegate to:
           - World Agent: Complex location design, detailed environments
           - Character Agent: NPC dialogue, character interactions  
           - Story Agent: Complex narrative events, story choices (include turn context!)
        
        GOAL: Provide an engaging, immersive response that makes the game world feel alive.
        Use your tools creatively to handle requests directly when possible, or delegate when you need 
        specialist expertise. Always give rich, descriptive responses that enhance the player experience
        and match the current story pacing phase.
        """,
        agent=create_game_coordinator_agent(),
        expected_output="An engaging response that either handles the request directly using available tools or coordinates with specialists as needed, with appropriate pacing for the current turn"
    )
    
    return task