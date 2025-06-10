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

class ParseUserActionTool(BaseTool):
    name: str = "parse_user_action"
    description: str = "Parse user input to determine what type of action they want to perform"
    
    def _run(self, user_input: str) -> str:
        """Parse user input and determine what type of action it represents."""
        user_input = user_input.lower().strip()
        
        # Determine action type
        if any(word in user_input for word in ["go", "move", "walk", "travel", "north", "south", "east", "west"]):
            action_type = "movement"
        elif any(word in user_input for word in ["talk", "speak", "say", "ask", "greet"]):
            action_type = "dialogue"
        elif any(word in user_input for word in ["look", "examine", "inspect", "search", "explore"]):
            action_type = "exploration"
        elif any(word in user_input for word in ["take", "get", "pick", "grab", "use"]):
            action_type = "interaction"
        elif any(word in user_input for word in ["help", "what", "where", "how", "who"]):
            action_type = "help"
        else:
            action_type = "general"
        
        result = {
            "action_type": action_type,
            "original_input": user_input,
            "requires_world": action_type in ["movement", "exploration", "interaction"],
            "requires_character": action_type in ["dialogue"],
            "requires_story": True,  # Story always needed for narrative coherence
            "priority": "high" if action_type == "movement" else "medium"
        }
        
        return json.dumps(result, indent=2)

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

def create_game_coordinator_agent():
    """Create the Coordinator Agent with tools"""
    
    game_coordinator = Agent(
        role="Coordinator Agent",
        goal="Intelligently orchestrate the entire game experience by analyzing user input and coordinating only the necessary agents",
        backstory="""You are the master game coordinator who ensures smooth gameplay by 
        intelligently analyzing what the user wants to do and determining which specialist agents 
        need to be involved. You avoid unnecessary work by only activating agents when their 
        expertise is truly needed. You understand the overall game flow and ensure efficient, 
        targeted responses that create engaging interactive fiction experiences.""",
        tools=[
            GetFullGameStateTool(),
            ParseUserActionTool(),
            GetCurrentSceneTool(),
            LogGameEventTool()
        ],
        verbose=True,
        allow_delegation=True  # This agent can delegate to others
    )
    
    return game_coordinator

def create_coordination_task(user_input: str):
    """Create a task for the Coordinator Agent"""
    
    task = Task(
        description=f"""
        INTELLIGENT COORDINATION TASK
        User Input: "{user_input}"
        
        Your job is to:
        1. Use parse_user_action to analyze what the user wants to do
        2. Use get_current_scene to understand the current context
        3. Use get_full_game_state to see the complete game state
        4. Determine which specialist agents (if any) need to be involved:
           - World Agent: Only for movement, exploration, or location changes
           - Character Agent: Only for character interactions or dialogue
           - Story Agent: Only when narrative events need to happen
        
        IMPORTANT: Be efficient! Don't involve agents unless truly necessary.
        For simple queries like "look around" or "status", handle them yourself.
        
        Create a comprehensive response that addresses the user's request.
        If you need specialist help, delegate specific tasks to the appropriate agents.
        """,
        agent=create_game_coordinator_agent(),
        expected_output="A comprehensive game response that efficiently addresses the user's input using only necessary agents"
    )
    
    return task