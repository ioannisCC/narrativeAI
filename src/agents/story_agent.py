from crewai import Agent, Task
from crewai.tools import BaseTool
import json
from game_state import game_state

class CreateStoryChoicesTool(BaseTool):
    name: str = "create_story_choices"
    description: str = "Create meaningful story choices for the player to make. Input should be simple text like '1) Do this 2) Do that 3) Do other'"
    
    def _run(self, choices_info: str) -> str:
        """Create story choices for the player."""
        try:
            # Always treat as simple string - no JSON parsing
            scenario = "current situation"
            
            # Split by numbered items
            if any(str(i) in choices_info for i in range(1, 6)):
                import re
                choices = re.findall(r'\d+[.)\s]+([^0-9]+?)(?=\d+[.)\s]|$)', choices_info)
                choices = [choice.strip().rstrip('.').rstrip(',') for choice in choices if choice.strip()]
            else:
                # Fallback: treat as single choice
                choices = [choices_info.strip()]
            
            if choices:
                game_state.add_story_event(f"Story choices created: {len(choices)} options")
                return f"✅ Created {len(choices)} choices: {choices}"
            else:
                return "⚠️ No valid choices found in input"
        except Exception as e:
            return f"❌ Error creating choices: {str(e)}"

class AdvanceStoryTool(BaseTool):
    name: str = "advance_story"
    description: str = "Advance the main storyline with new events"
    
    def _run(self, story_event: str) -> str:
        """Advance the main story with a new event."""
        game_state.add_story_event(story_event)
        return f"Story advanced: {story_event}"

class GetStoryContextTool(BaseTool):
    name: str = "get_story_context"
    description: str = "Get current story context including events, player choices, and turn progression"
    
    def _run(self) -> str:
        """Get current story context and player choices"""
        story_data = game_state.get_state()["story"]
        turn_info = game_state.get_turn_info()
        
        context = {
            "story": story_data,
            "turn_info": turn_info,
            "pacing_guidance": self._get_pacing_guidance(turn_info)
        }
        
        return json.dumps(context, indent=2)
    
    def _get_pacing_guidance(self, turn_info):
        """Get pacing guidance based on current turn progress"""
        phase = turn_info["phase"]
        current = turn_info["current_turn"]
        max_turns = turn_info["max_turns"]
        remaining = turn_info["turns_remaining"]
        
        if phase == "beginning":
            return f"Early adventure (Turn {current}/{max_turns}). Focus on world-building, discovery, and setting up the quest."
        elif phase == "middle":
            return f"Mid-adventure (Turn {current}/{max_turns}). Develop challenges, character interactions, and plot complications."
        elif phase == "late":
            return f"Late adventure (Turn {current}/{max_turns}). Build toward climax, increase stakes, prepare for resolution."
        else:  # climax
            if remaining <= 1:
                return f"FINAL TURN ({current}/{max_turns}). This must be the epic conclusion! Resolve all plot threads and provide satisfying ending."
            else:
                return f"Climax phase (Turn {current}/{max_turns}). Major dramatic moments, final challenges, approaching resolution."

class RecordPlayerChoiceTool(BaseTool):
    name: str = "record_player_choice"
    description: str = "Record a player's choice and its consequences. Input should be simple text like 'Player chose option 2'"
    
    def _run(self, choice_info: str) -> str:
        """Record a choice made by the player."""
        try:
            # Always treat as simple string
            choice = choice_info.strip()
            
            # Record in game state
            game_state.add_choice_made(choice)
            game_state.add_story_event(f"Player decision recorded: {choice}")
            
            return f"✅ Recorded player choice: {choice}"
        except Exception as e:
            return f"❌ Error recording choice: {str(e)}"

class GetStorySummaryTool(BaseTool):
    name: str = "get_story_summary"
    description: str = "Get a summary of the current story state"
    
    def _run(self) -> str:
        """Generate a summary of the current story state"""
        state = game_state.get_state()
        
        summary = {
            "current_chapter": state["story"]["current_chapter"],
            "player_location": state["player"]["location"],
            "recent_events": state["story"]["events"][-3:],  # Last 3 events
            "choices_made": len(state["story"]["choices_made"]),
            "characters_met": list(state["characters"].keys()),
            "locations_discovered": list(state["world"]["locations"].keys())
        }
        
        return json.dumps(summary, indent=2)

class CreateStoryNarrativeTool(BaseTool):
    name: str = "create_story_narrative"
    description: str = "Generate a beautiful narrative summary of the player's adventure using all game data"
    
    def _run(self) -> str:
        """Create a comprehensive narrative summary of the adventure"""
        summary_data = game_state.get_story_summary_data()
        turn_info = summary_data['turn_info']
        
        # Create a beautiful narrative summary with turn awareness
        narrative = f"""In the span of {summary_data['session_info']['duration_minutes']} minutes of adventure, {summary_data['player']['name']} has embarked on a mystical journey through an enchanted forest realm.

The tale began with {summary_data['player']['name']}'s awakening in a mysterious forest clearing, where ancient trees whispered secrets and golden sunlight painted magical patterns through the canopy. From this verdant sanctuary, our brave adventurer ventured forth to explore the wonders that lay beyond.

"""
        
        # Add turn progression context
        if turn_info['current_turn'] > 0:
            phase_desc = {
                "beginning": "beginning their epic quest",
                "middle": "deep in the heart of their adventure", 
                "late": "approaching the climax of their journey",
                "climax": "in the final, pivotal moments of their saga"
            }
            narrative += f"Currently in Turn {turn_info['current_turn']} of {turn_info['max_turns']}, {summary_data['player']['name']} finds themselves {phase_desc[turn_info['phase']]}"
            
            if turn_info['turns_remaining'] <= 1:
                narrative += ", standing at the threshold of their adventure's ultimate conclusion.\n\n"
            elif turn_info['turns_remaining'] <= 2:
                narrative += f", with only {turn_info['turns_remaining']} turns remaining to fulfill their destiny.\n\n"
            else:
                narrative += f", with {turn_info['turns_remaining']} turns still ahead to shape their legacy.\n\n"
        
        # Add locations explored
        if len(summary_data['locations_visited']) > 1:
            narrative += f"Through courage and curiosity, {summary_data['player']['name']} has discovered {len(summary_data['locations_visited'])} mystical locations: "
            narrative += ", ".join([loc.replace('_', ' ').title() for loc in summary_data['locations_visited']])
            narrative += ". Each place held its own mysteries and wonders, contributing to the tapestry of this unfolding adventure.\n\n"
        
        # Add story events
        if summary_data['story_events']:
            narrative += "Key moments in this epic tale include:\n"
            for event in summary_data['story_events']:
                if event != "The adventure begins in a mysterious forest clearing":
                    narrative += f"• {event}\n"
            narrative += "\n"
        
        # Add characters if any
        if summary_data['characters_met']:
            narrative += f"Along the way, {summary_data['player']['name']} has encountered remarkable beings: "
            narrative += ", ".join(summary_data['characters_met'])
            narrative += ", each adding depth and intrigue to the journey.\n\n"
        
        # Add choices if any
        if summary_data['choices_made']:
            narrative += f"Through {len(summary_data['choices_made'])} pivotal decisions, our hero has shaped the course of destiny, with each choice rippling through the fabric of this mystical realm.\n\n"
        
        # Conclude based on turn progression
        if turn_info['phase'] == "climax" and turn_info['turns_remaining'] <= 1:
            narrative += f"As the final moments of this adventure unfold, {summary_data['player']['name']} stands poised to write the ultimate chapter of their legend. Whatever happens next will determine how this tale ends - in triumph, wisdom, or perhaps something entirely unexpected."
        elif turn_info['phase'] == "late":
            narrative += f"As the adventure builds toward its crescendo, {summary_data['player']['name']} can sense that momentous events are approaching. The choices made in the remaining turns will determine the fate of this mystical realm."
        else:
            narrative += f"As Chapter {summary_data['current_chapter']} continues to unfold, {summary_data['player']['name']} stands ready to face whatever wonders and challenges await in this enchanted world. The adventure has only just begun, and countless possibilities stretch ahead like paths through an endless, magical forest."
        
        return narrative

def create_story_director_agent():
    """Create the Story Agent with tools"""
    
    story_director = Agent(
        role="Story Agent",
        goal="Create compelling narrative arcs and meaningful player choices that drive the story forward with proper pacing",
        backstory="""You are a master storyteller who crafts engaging interactive narratives. 
        You understand pacing, character development, and how player choices affect story outcomes. 
        You create meaningful decisions that impact the game world and story progression.
        
        IMPORTANT: When using tools, always pass simple text strings, never JSON objects.
        Example: create_story_choices("1) Do this 2) Do that 3) Other option")
        NOT: create_story_choices({"choices_info": "text"})
        
        You are aware of turn progression and adjust story pacing accordingly.""",
        tools=[
            CreateStoryChoicesTool(),
            AdvanceStoryTool(),
            GetStoryContextTool(),
            RecordPlayerChoiceTool(),
            GetStorySummaryTool(),
            CreateStoryNarrativeTool()
        ],
        verbose=True,
        allow_delegation=False
    )
    
    return story_director

def create_story_task(user_input: str, specific_request: str = None):
    """Create a task for the Story Agent"""
    
    request = specific_request or f"Handle narrative aspects of: {user_input}"
    
    # Get turn context for story pacing
    turn_info = game_state.get_turn_info()
    turn_context = ""
    
    if turn_info['current_turn'] > 0:
        turn_context = f"""
        
        TURN AWARENESS: Currently Turn {turn_info['current_turn']}/{turn_info['max_turns']} ({turn_info['phase']} phase)
        - Turns remaining: {turn_info['turns_remaining']}
        - {'⚠️ FINAL TURN - Must conclude adventure!' if turn_info['turns_remaining'] <= 1 else ''}
        
        Use get_story_context tool to get detailed pacing guidance.
        """
    
    task = Task(
        description=f"""
        {request}
        {turn_context}
        
        You have access to these tools:
        - create_story_choices: Create meaningful choices for players (consider turn pacing)
        - advance_story: Add new story events (match current story phase)
        - get_story_context: Check current narrative state and get pacing guidance
        - record_player_choice: Track player decisions
        - get_story_summary: Get overview of story progress
        - create_story_narrative: Generate beautiful narrative summaries
        
        Use your tools to create engaging narrative moments and meaningful player agency
        that matches the current turn progression and story phase.
        """,
        agent=create_story_director_agent(),
        expected_output="Story progression with events and choices that enhance the narrative and match turn pacing"
    )
    
    return task