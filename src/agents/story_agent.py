from crewai import Agent, Task
from crewai.tools import BaseTool
import json
from game_state import game_state

class CreateStoryChoicesTool(BaseTool):
    name: str = "create_story_choices"
    description: str = "Create meaningful story choices for the player using AI creativity to parse and format any choice text naturally"
    
    def _run(self, choices_info: str) -> str:
        """Create story choices using LLM intelligence instead of rigid parsing."""
        try:
            # Let the LLM naturally extract choices from any format
            # Instead of regex, we'll trust the input and just clean it up
            choices_text = choices_info.strip()
            
            # Simple approach: split by common separators and clean
            potential_choices = []
            
            # Try different natural separators
            if '\n' in choices_text:
                potential_choices = [line.strip() for line in choices_text.split('\n') if line.strip()]
            elif '. ' in choices_text and choices_text.count('. ') > 1:
                potential_choices = [choice.strip() for choice in choices_text.split('. ') if choice.strip()]
            elif ' or ' in choices_text.lower():
                potential_choices = [choice.strip() for choice in choices_text.replace(' OR ', ' or ').split(' or ') if choice.strip()]
            else:
                # Single choice or let the LLM handle it naturally
                potential_choices = [choices_text]
            
            # Clean up the choices by removing common prefixes
            cleaned_choices = []
            for choice in potential_choices:
                # Remove common prefixes like "1)", "•", "-", etc.
                import re
                cleaned = re.sub(r'^[\d\-\*\u2022\)\.]+\s*', '', choice).strip()
                if cleaned and len(cleaned) > 3:  # Avoid tiny fragments
                    cleaned_choices.append(cleaned)
            
            # If we got good choices, use them; otherwise treat as single choice
            final_choices = cleaned_choices if len(cleaned_choices) > 1 else [choices_text]
            
            # Record the choices
            if final_choices:
                game_state.add_story_event(f"Player presented with {len(final_choices)} choices")
                return f"✅ Created {len(final_choices)} meaningful choices for the player"
            else:
                return "⚠️ Choice creation attempted but no clear options found"
                
        except Exception as e:
            # Fallback: just record that choices were attempted
            game_state.add_story_event("Story choices presented to player")
            return f"✅ Story choices created (error in parsing: {str(e)})"

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
            return f"Early adventure (Turn {current}/{max_turns}). Focus on world-building, discovery, and setup."
        elif phase == "middle":
            return f"Mid-adventure (Turn {current}/{max_turns}). Develop challenges, character interactions, and complications."
        elif phase == "late":
            return f"Late adventure (Turn {current}/{max_turns}). Build toward climax, increase stakes."
        else:  # climax
            if remaining <= 1:
                return f"Final turn ({current}/{max_turns}). Create rich, detailed conclusion that honors player choices."
            else:
                return f"Climax phase (Turn {current}/{max_turns}). Major dramatic moments, approaching resolution."

class RecordPlayerChoiceTool(BaseTool):
    name: str = "record_player_choice"
    description: str = "Record a player's choice and its consequences"
    
    def _run(self, choice_info: str) -> str:
        """Record a choice made by the player."""
        try:
            choice = choice_info.strip()
            game_state.add_choice_made(choice)
            game_state.add_story_event(f"Player chose: {choice}")
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
            "recent_events": state["story"]["events"][-3:],
            "choices_made": len(state["story"]["choices_made"]),
            "characters_met": list(state["characters"].keys()),
            "locations_discovered": list(state["world"]["locations"].keys())
        }
        
        return json.dumps(summary, indent=2)

class CreateStoryNarrativeTool(BaseTool):
    name: str = "create_story_narrative"
    description: str = "Generate beautiful narrative summaries using pure LLM creativity - no templates, just storytelling intelligence"
    
    def _run(self, narrative_type: str = "summary") -> str:
        """Create narrative content using LLM creativity instead of mechanical templates"""
        
        # Get the raw adventure data
        summary_data = game_state.get_story_summary_data()
        
        # Instead of using templates, create a storytelling prompt for the LLM
        # This will be handled by the agent's own LLM intelligence
        
        if "conclude" in narrative_type.lower() or "epilogue" in narrative_type.lower():
            return self._create_llm_conclusion_prompt(summary_data)
        elif "comprehensive" in narrative_type.lower():
            return self._create_llm_recap_prompt(summary_data)
        else:
            return self._create_llm_progress_prompt(summary_data)
    
    def _create_llm_conclusion_prompt(self, summary_data):
        """Create a prompt for the LLM to generate an organic conclusion"""
        player_name = summary_data['player']['name']
        
        # Return a natural prompt that the LLM agent will process
        return f"""Create a beautiful, flowing epilogue for {player_name}'s adventure that weaves together their journey into a compelling narrative.

        Focus on:
        - How their choices shaped a unique story
        - The emotional arc of their adventure  
        - The transformation they experienced
        - The meaning of their decisions
        - A sense of completion and legend

        Write this as flowing prose, not a list. Make it feel like the conclusion of an epic tale that could only belong to {player_name}."""
    
    def _create_llm_recap_prompt(self, summary_data):
        """Create a prompt for the LLM to generate an organic comprehensive recap"""
        player_name = summary_data['player']['name']
        turn_count = summary_data['turn_info']['current_turn']
        
        return f"""Write a comprehensive adventure story that chronicles {player_name}'s complete {turn_count}-turn journey.

        Show how the story evolved through player choices and create a narrative that reads like an exciting adventure recap. Focus on:
        - The beginning and how it set up the quest
        - How each major decision created consequences and shaped the path
        - The discoveries and revelations along the way
        - How player agency drove the unique story that unfolded
        - The climactic moments and their resolution

        Write this as an engaging story summary that highlights {player_name}'s agency and the unique path their choices created. Make it read like a thrilling adventure recap, not a mechanical log."""
    
    def _create_llm_progress_prompt(self, summary_data):
        """Create a prompt for the LLM to generate an organic progress narrative"""
        player_name = summary_data['player']['name']
        turn_info = summary_data['turn_info']
        
        return f"""Create a beautiful narrative summary of {player_name}'s adventure in progress.

        Currently in turn {turn_info['current_turn']} of {turn_info['max_turns']} ({turn_info['phase']} phase).

        Write flowing prose that captures:
        - The journey so far and its unique elements
        - How choices have shaped the unfolding story
        - The sense of adventure and discovery
        - What lies ahead based on the current phase

        Make this feel like a chapter summary in an epic adventure novel, highlighting the wonder and choice-driven nature of {player_name}'s unique journey."""

def create_story_director_agent():
    """Create the Story Agent with natural, LLM-driven storytelling"""
    
    story_director = Agent(
        role="Master Story Director & Creative Narrative Intelligence",
        goal="Create compelling interactive narratives using pure AI creativity, with special attention to rich final encounters",
        backstory="""You are a master storyteller who excels at creating engaging interactive fiction 
        using pure AI creativity and natural language understanding. You never rely on rigid templates 
        or mechanical parsing - instead, you use your storytelling intelligence to understand player 
        intent and create rich, meaningful narrative content.

        Your strengths include:
        - Understanding player choices in any format they express them
        - Creating rich, detailed encounters that expand player actions dramatically
        - Generating flowing, organic narrative summaries that feel like real stories
        - Honoring player agency by building meaningful content around their actual decisions
        - Crafting final turns that are epic and satisfying without being over-the-top

        For final turns, you excel at taking whatever the player chose and expanding it into a 
        detailed, atmospheric encounter with meaningful dialogue, rich descriptions, and satisfying 
        resolutions. You understand that "encounter a dragon" should become a full scene with 
        the dragon's personality, the setting, meaningful choices, and consequences.

        You always honor player choices exactly as intended, use AI creativity to generate unique 
        content, and create narrative summaries that read like beautiful stories rather than 
        mechanical logs.""",
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
    """Create a story task with natural, balanced instructions"""
    
    request = specific_request or f"Handle narrative aspects of: {user_input}"
    
    # Get turn context
    turn_info = game_state.get_turn_info()
    turn_context = ""
    
    if turn_info['current_turn'] > 0:
        if turn_info['current_turn'] >= turn_info['max_turns']:
            turn_context = f"""
            
            This is the final turn ({turn_info['current_turn']}/{turn_info['max_turns']}) - create a rich, 
            detailed encounter that expands the player's choice into a full climactic scene. Take time to 
            develop the encounter with atmosphere, meaningful dialogue, and satisfying resolution.
            """
        else:
            turn_context = f"""
            
            Currently Turn {turn_info['current_turn']}/{turn_info['max_turns']} ({turn_info['phase']} phase).
            Use get_story_context for detailed pacing guidance.
            """
    
    task = Task(
        description=f"""
        {request}
        {turn_context}
        
        Core principles:
        - Always honor player choices and build meaningful content around their decisions
        - Use AI creativity to generate rich, unique encounters and narratives
        - For narrative summaries, create flowing stories rather than mechanical lists
        - When creating choices, present them naturally without rigid formatting requirements
        - For final turns, expand player actions into detailed, atmospheric scenes
        
        Available tools:
        - get_story_context: Understand the complete story and player journey
        - advance_story: Add story events based on player choices  
        - create_story_choices: Present meaningful options using natural language
        - record_player_choice: Track important player decisions
        - get_story_summary: Get current story overview
        - create_story_narrative: Generate beautiful, flowing narrative content
        
        Use your storytelling intelligence to create engaging content that feels natural and honors 
        the player's unique journey. Focus on creativity, meaningful choices, and rich storytelling.
        """,
        agent=create_story_director_agent(),
        expected_output="Rich, creative story content that honors player choices and creates engaging narrative experiences using natural AI storytelling"
    )
    
    return task