from crewai import Agent, Task
from crewai.tools import BaseTool
import json
from game_state import game_state

class CreateStoryChoicesTool(BaseTool):
    name: str = "create_story_choices"
    description: str = "Create meaningful story choices for the player to make"
    
    def _run(self, choices_info: str) -> str:
        """Create story choices for the player."""
        try:
            # Handle both JSON and simple string input
            if isinstance(choices_info, str):
                try:
                    # Try to parse as JSON first
                    data = json.loads(choices_info)
                    scenario = data.get("scenario", "current situation")
                    choices = data.get("choices", [])
                except json.JSONDecodeError:
                    # If not JSON, treat as simple string with choices
                    scenario = "current situation"
                    # Split by semicolons or numbered items
                    if ";" in choices_info:
                        choices = [choice.strip() for choice in choices_info.split(";")]
                    elif any(str(i) in choices_info for i in range(1, 6)):
                        # Handle numbered choices like "1. choice1 2. choice2"
                        import re
                        choices = re.findall(r'\d+\.\s*([^0-9]+?)(?=\d+\.|$)', choices_info)
                        choices = [choice.strip() for choice in choices]
                    else:
                        choices = [choices_info]
            else:
                scenario = "current situation"
                choices = [str(choices_info)]
            
            game_state.add_story_event(f"Choices created for: {scenario}")
            return f"Created {len(choices)} choices for scenario: {scenario}. Choices: {choices}"
        except Exception as e:
            return f"Error creating choices: {str(e)}"

class AdvanceStoryTool(BaseTool):
    name: str = "advance_story"
    description: str = "Advance the main storyline with new events"
    
    def _run(self, story_event: str) -> str:
        """Advance the main story with a new event."""
        game_state.add_story_event(story_event)
        return f"Story advanced: {story_event}"

class GetStoryContextTool(BaseTool):
    name: str = "get_story_context"
    description: str = "Get current story context including events and player choices"
    
    def _run(self) -> str:
        """Get current story context and player choices"""
        story_data = game_state.get_state()["story"]
        return json.dumps(story_data, indent=2)

class RecordPlayerChoiceTool(BaseTool):
    name: str = "record_player_choice"
    description: str = "Record a player's choice and its consequences"
    
    def _run(self, choice_info: str) -> str:
        """Record a choice made by the player."""
        try:
            # Handle both JSON and simple string input
            if isinstance(choice_info, str):
                try:
                    data = json.loads(choice_info)
                    choice = data.get("choice")
                    consequence = data.get("consequence", "")
                except json.JSONDecodeError:
                    # If not JSON, treat as simple choice string
                    choice = choice_info
                    consequence = ""
            else:
                choice = str(choice_info)
                consequence = ""
            
            game_state.add_choice_made(choice)
            if consequence:
                game_state.add_story_event(f"Choice consequence: {consequence}")
            
            return f"Recorded choice: {choice}"
        except Exception as e:
            return f"Error recording choice: {str(e)}"

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
    description: str = "Generate a narrative summary of the player's adventure using all game data"
    
    def _run(self) -> str:
        """Create a comprehensive narrative summary of the adventure"""
        summary_data = game_state.get_story_summary_data()
        
        narrative_prompt = f"""
        Create an engaging narrative summary of this interactive fiction adventure:
        
        SESSION INFO:
        - Duration: {summary_data['session_info']['duration_minutes']} minutes
        - Player: {summary_data['player']['name']}
        - Current Location: {summary_data['player']['location']}
        
        LOCATIONS EXPLORED:
        {', '.join(summary_data['locations_visited'])}
        
        CHARACTERS MET:
        {', '.join(summary_data['characters_met']) if summary_data['characters_met'] else 'None yet'}
        
        STORY EVENTS:
        {chr(10).join(summary_data['story_events'])}
        
        CHOICES MADE:
        {chr(10).join(summary_data['choices_made']) if summary_data['choices_made'] else 'No major choices yet'}
        
        Write a compelling 2-3 paragraph narrative that captures the essence of this adventure,
        highlighting key moments, character interactions, and the player's journey so far.
        Make it feel like an epic tale!
        """
        
        # Log the summarization request
        game_state.log_event("Story narrative summary requested")
        
        return narrative_prompt

def create_story_director_agent():
    """Create the Story Agent with tools"""
    
    story_director = Agent(
        role="Story Agent",
        goal="Create compelling narrative arcs and meaningful player choices that drive the story forward",
        backstory="""You are a master storyteller who crafts engaging interactive narratives. 
        You understand pacing, character development, and how player choices affect story outcomes. 
        You create meaningful decisions that impact the game world and story progression.
        You have tools to manage story events, choices, and narrative progression.""",
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
    
    task = Task(
        description=f"""
        {request}
        
        You have access to these tools:
        - create_story_choices: Create meaningful choices for players
        - advance_story: Add new story events
        - get_story_context: Check current narrative state
        - record_player_choice: Track player decisions
        - get_story_summary: Get overview of story progress
        
        Use your tools to create engaging narrative moments and meaningful player agency.
        """,
        agent=create_story_director_agent(),
        expected_output="Story progression with events and choices that enhance the narrative"
    )
    
    return task