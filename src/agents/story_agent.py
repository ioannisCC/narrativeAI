"""
Story Agent - Narrative Director & Plot Weaver
Responsible for main storyline, plot progression, and meaningful choices
"""

from crewai import Agent
from typing import List, Dict, Any


class StoryAgent:
    """
    The Story Agent manages the main narrative, creates meaningful choices,
    and ensures story progression. This agent focuses on plot development,
    dramatic tension, and consequence management.
    """
    
    def __init__(self, llm=None):
        self.agent = Agent(
            role='Narrative Director & Plot Weaver',
            goal='''Create compelling storylines with meaningful choices, manage plot 
                    progression, and ensure that player decisions have interesting 
                    consequences. Build dramatic tension and narrative satisfaction.''',
            backstory='''You are a master storyteller who understands narrative 
                        structure, pacing, and the art of meaningful choice. You've 
                        studied classic literature, modern interactive fiction, and 
                        game narrative design. You know how to create stories where 
                        every choice matters and leads to interesting consequences. 
                        You excel at building tension, creating satisfying plot twists, 
                        and ensuring that stories feel both surprising and inevitable.''',
            verbose=True,
            allow_delegation=False,
            llm=llm
        )
    
    def develop_plot_progression(self, current_situation: str, 
                               player_choice: str,
                               story_history: List[str]) -> str:
        """
        Advance the main plot based on player choice and story history
        
        Args:
            current_situation: The current story state
            player_choice: What the player just chose to do
            story_history: List of previous story beats
            
        Returns:
            Next plot development and story progression
        """
        history_context = "; ".join(story_history[-3:])  # Last 3 story beats
        
        task_description = f"""
        Develop the next plot progression based on the player's choice.
        
        Current Situation: {current_situation}
        Player Choice: {player_choice}
        Recent Story History: {history_context}
        
        Create:
        - Immediate consequence of the player's choice
        - How this advances or changes the main plot
        - New story elements or complications introduced
        - Building tension or resolution
        - Setup for the next meaningful choice
        
        Ensure the progression feels natural and that choices have weight.
        Keep it engaging and build toward dramatic moments.
        """
        
        return task_description
    
    def generate_meaningful_choices(self, current_situation: str, 
                                  character_context: str,
                                  world_context: str) -> str:
        """
        Create 2-4 meaningful choices for the player
        
        Args:
            current_situation: Current story state
            character_context: Available characters and relationships
            world_context: Environmental factors and possibilities
            
        Returns:
            List of meaningful choice options with consequences
        """
        task_description = f"""
        Generate 3-4 meaningful choices for the player in the current situation.
        
        Current Situation: {current_situation}
        Available Characters: {character_context}
        Environmental Factors: {world_context}
        
        For each choice, provide:
        - Clear action description (1 sentence)
        - What type of consequence this might lead to
        - How it might affect relationships or plot
        
        Requirements:
        - Each choice should lead to different outcomes
        - Include variety: action, diplomacy, exploration, creative solutions
        - Make choices feel meaningful, not arbitrary
        - Avoid "obvious correct answer" scenarios
        
        Format as numbered list with brief consequence hints.
        """
        
        return task_description
    
    def manage_story_consequences(self, choice_made: str, 
                                immediate_outcome: str,
                                story_state: Dict[str, Any]) -> str:
        """
        Determine longer-term consequences of player choices
        
        Args:
            choice_made: The choice the player made
            immediate_outcome: What happened immediately
            story_state: Current story state and variables
            
        Returns:
            Longer-term consequences and story impacts
        """
        task_description = f"""
        Determine the broader consequences of the player's choice.
        
        Player Choice: {choice_made}
        Immediate Outcome: {immediate_outcome}
        Current Story State: {story_state}
        
        Consider:
        - How this choice affects the overall story arc
        - What opportunities or problems this creates for later
        - Character relationship changes
        - World state changes
        - Potential plot branches this opens or closes
        
        Think about both positive and negative consequences that feel earned.
        """
        
        return task_description
    
    def create_story_climax(self, story_history: List[str], 
                          character_relationships: Dict[str, str],
                          player_choices_summary: str) -> str:
        """
        Create a climactic moment based on the accumulated story
        
        Args:
            story_history: Full story progression so far
            character_relationships: Current state of all relationships
            player_choices_summary: Summary of key player decisions
            
        Returns:
            Climactic scene that pays off the story setup
        """
        task_description = f"""
        Create a climactic scene that brings together the story elements.
        
        Story So Far: {story_history}
        Character Relationships: {character_relationships}
        Key Player Choices: {player_choices_summary}
        
        Design a climactic moment that:
        - Pays off the major story threads
        - Reflects the consequences of player choices
        - Involves characters in meaningful ways
        - Creates a satisfying dramatic peak
        - Sets up a resolution that feels earned
        
        Make the climax feel like the natural result of everything that came before.
        """
        
        return task_description