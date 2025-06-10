from crewai import Agent, Task
from crewai.tools import BaseTool
import json
from game_state import game_state

class GetFullGameStateTool(BaseTool):
    name: str = "get_full_game_state"
    description: str = "Get the complete current game state for coordination"
    
    def _run(self) -> str:
        """Get the complete current game state from single source of truth"""
        return game_state.to_json()

class GetCurrentSceneTool(BaseTool):
    name: str = "get_current_scene"
    description: str = "Get detailed description of the current game scene from game_state"
    
    def _run(self) -> str:
        """Get description of current game scene from single source of truth"""
        state = game_state.get_state()
        current_location = state["player"]["location"]
        
        if not current_location:
            return json.dumps({"error": "No current location set"}, indent=2)
            
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
        """Log an important game event to game_state"""
        game_state.log_event(event)
        return f"✅ Logged: {event}"

class UpdatePlayerLocationTool(BaseTool):
    name: str = "update_player_location"
    description: str = "Move the player to a new location (use only if location exists)"
    
    def _run(self, location_name: str) -> str:
        """Move player to a new location in game_state"""
        try:
            # Check if location exists first
            if not game_state.location_exists(location_name):
                return f"❌ Cannot move to '{location_name}' - location does not exist in game_state"
                
            game_state.set_current_location(location_name)
            return f"✅ Player moved to: {location_name}"
        except Exception as e:
            return f"❌ Error moving player: {str(e)}"

class CreateBasicLocationTool(BaseTool):
    name: str = "create_basic_location"
    description: str = "Create a simple location if it doesn't exist (for basic coordinator needs)"
    
    def _run(self, location_info: str) -> str:
        """Create a basic location and save to game_state"""
        try:
            # Handle simple name: description format
            if ":" in location_info:
                parts = location_info.split(":", 1)
                name = parts[0].strip().lower().replace(" ", "_")
                description = parts[1].strip()
            else:
                name = location_info.strip().lower().replace(" ", "_")
                description = f"A new area discovered during your adventure."
            
            data = {
                "name": name,
                "description": description,
                "exits": ["back"],
                "items": []
            }
            
            # Save to game_state using the proper method
            game_state.add_location(name, data)
            return f"✅ Created basic location '{name}' in game_state"
        except Exception as e:
            return f"❌ Error creating location: {str(e)}"

class RecordPlayerChoiceTool(BaseTool):
    name: str = "record_player_choice"
    description: str = "Record and honor a critical player choice that must be followed"
    
    def _run(self, choice: str) -> str:
        """Record a critical player choice that MUST be honored"""
        try:
            game_state.add_choice_made(choice)
            game_state.add_story_event(f"CRITICAL PLAYER CHOICE: {choice}")
            return f"✅ RECORDED CRITICAL CHOICE: {choice} - MUST BE HONORED"
        except Exception as e:
            return f"❌ Error recording choice: {str(e)}"

class CheckLocationExistsTool(BaseTool):
    name: str = "check_location_exists"
    description: str = "Check if a location exists in the game world before trying to move there"
    
    def _run(self, location_name: str) -> str:
        """Check if a location exists in game_state"""
        exists = game_state.location_exists(location_name)
        if exists:
            return f"✅ Location '{location_name}' exists in game_state"
        else:
            available_locations = list(game_state.get_all_locations().keys())
            return f"❌ Location '{location_name}' does not exist. Available locations: {available_locations}"

class GetWorldLocationsTool(BaseTool):
    name: str = "get_world_locations"
    description: str = "Get a list of all available locations in the game world"
    
    def _run(self) -> str:
        """Get all locations from game_state"""
        locations = game_state.get_all_locations()
        location_summary = {}
        
        for loc_name, loc_data in locations.items():
            location_summary[loc_name] = {
                "description": loc_data.get("description", "")[:100] + "..." if len(loc_data.get("description", "")) > 100 else loc_data.get("description", ""),
                "exits": loc_data.get("exits", []),
                "item_count": len(loc_data.get("items", []))
            }
        
        return json.dumps(location_summary, indent=2)

def create_game_coordinator_agent():
    """Create the Coordinator Agent with enhanced storytelling focus and game_state integration"""
    
    game_coordinator = Agent(
        role="Master Game Coordinator & Story Director",
        goal="Create engaging, rich interactive fiction experiences with meaningful choices and compelling narratives using game_state as single source of truth",
        backstory="""You are a master storyteller and game coordinator who creates immersive, engaging interactive fiction. 

        CORE PHILOSOPHY:
        - game_state is the SINGLE SOURCE OF TRUTH - all world data lives there
        - Every scene should have narrative tension, mystery, or intrigue
        - Players should always have meaningful choices that impact the story
        - Delegate to specialists when you need rich content beyond basic descriptions
        - Simple movement should still result in engaging, story-driven responses
        
        GAME_STATE INTEGRATION:
        - Always check current scene and game state before responding
        - Verify locations exist before moving players
        - Use tools to read from and write to the shared game_state
        - Remember that World Agent creates locations, you coordinate access to them
        
        STORYTELLING PRIORITIES:
        1. ALWAYS provide rich, atmospheric descriptions
        2. Create story hooks, mysteries, and interesting encounters
        3. Offer meaningful choices when appropriate
        4. Delegate to Story Agent for complex narrative development
        5. Delegate to World Agent for detailed environment creation
        6. Delegate to Character Agent for NPC interactions
        
        PLAYER AGENCY RULES (SACRED):
        - Player choices are SACRED - if a player chooses option 3, you MUST follow option 3
        - Record all important player choices using record_player_choice tool
        - When players make numbered choices, acknowledge and follow their exact choice
        
        You have access to game context, player state, location data, story progression, and turn information
        through your tools that read from the single source of truth (game_state).
        Your goal is to create engaging, choice-driven narratives that feel like a real adventure.""",
        tools=[
            GetFullGameStateTool(),
            GetCurrentSceneTool(),
            LogGameEventTool(),
            UpdatePlayerLocationTool(),
            CreateBasicLocationTool(),
            RecordPlayerChoiceTool(),
            CheckLocationExistsTool(),
            GetWorldLocationsTool()
        ],
        verbose=True,
        allow_delegation=True
    )
    
    return game_coordinator

def create_coordination_task(user_input: str):
    """Create a smart coordination task focused on rich storytelling with game_state integration"""
    
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
        - Beginning phase (1-1): World-building, discovery, setup mysterious hooks
        - Middle phase (2-3): Challenges, character development, meaningful choices
        - Late phase (4): Build toward climax, increase stakes, major decisions
        - Climax phase (5): Epic conclusion, resolve all plot threads
        
        Adjust your response and delegations to match the current story phase.
        """
    
    # Check if this is a player choice from previous options
    choice_context = ""
    if any(word in user_input.lower() for word in ['option', 'choice', 'choose', '1)', '2)', '3)', '4)']):
        choice_context = """
        🚨 PLAYER CHOICE DETECTED! 🚨
        This appears to be a player choosing from previous options.
        Use record_player_choice tool to record this choice.
        CRITICAL: You MUST honor their exact choice - do not deviate or substitute.
        """
    
    task = Task(
        description=f"""
        ENHANCED STORYTELLING COORDINATION TASK WITH GAME_STATE INTEGRATION
        User Input: "{user_input}"
        {turn_context}
        {choice_context}
        
        YOUR MISSION: Create engaging, choice-driven interactive fiction that feels alive and immersive,
        using game_state as the single source of truth for all world information.
        
        DECISION PROCESS:
        1. Use get_current_scene and/or get_full_game_state to understand context from game_state
        2. Consider turn progression for appropriate story pacing
        3. If this is a player choice, use record_player_choice tool and HONOR their choice
        4. For movement commands, use check_location_exists before attempting to move
        5. For SIMPLE requests, handle directly BUT make them engaging:
           - Movement commands → Create atmospheric descriptions, story hooks, discoveries
           - Basic exploration → Rich environmental storytelling with mysteries/intrigue
           - Status requests → Provide information with narrative flair
        6. For COMPLEX/RICH content needs, delegate to specialists:
           - World Agent: Detailed locations, complex environments, atmospheric settings
           - Character Agent: NPCs, dialogue, character interactions, personalities
           - Story Agent: Plot development, meaningful choices, story progression, narrative events
        
        GAME_STATE INTEGRATION RULES:
        ✅ DO use get_current_scene to understand what's in the current location
        ✅ DO use check_location_exists before moving players
        ✅ DO use get_world_locations to see what areas are available
        ✅ DO delegate to World Agent if new locations need to be created
        ✅ DO read from game_state as the single source of truth
        
        STORYTELLING GUIDELINES:
        ✅ DO create rich, atmospheric descriptions even for simple movement
        ✅ DO introduce story elements: mysteries, discoveries, interesting details
        ✅ DO provide meaningful choices when appropriate (delegate to Story Agent)
        ✅ DO create narrative tension and intrigue
        ✅ DO make every response feel like part of an adventure
        
        ❌ DON'T give bland, basic descriptions like "A new area of the forest"
        ❌ DON'T just move the player without adding story elements
        ❌ DON'T miss opportunities to create engaging content
        ❌ DON'T ignore player choices or substitute different actions
        ❌ DON'T assume locations exist - check first using tools
        
        DELEGATION TRIGGERS:
        - "Need rich location details" → World Agent
        - "Need story progression/choices" → Story Agent  
        - "Need character interactions" → Character Agent
        - "Simple movement but want atmospheric description" → Handle directly with rich content
        
        GOAL: Every response should feel engaging and story-driven, whether handled directly or delegated.
        Player choices are SACRED and must be honored exactly as chosen.
        Always use game_state as the single source of truth for world information.
        """,
        agent=create_game_coordinator_agent(),
        expected_output="An engaging, story-driven response that either handles the request with rich content or delegates to specialists for complex narrative development, using game_state as single source of truth"
    )
    
    return task