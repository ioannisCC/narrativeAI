from crewai import Agent
from typing import Dict, List, Any


class CharacterAgent:
    """
    The Character Agent creates and manages NPCs (Non-Player Characters),
    their personalities, dialogue, and interactions. This agent focuses
    on bringing characters to life and creating meaningful relationships.
    """
    
    def __init__(self, llm=None):
        self.agent = Agent(
            role='Character Creator & Personality Manager',
            goal='''Create memorable, believable characters with distinct personalities, 
                    motivations, and dialogue patterns. Manage character interactions 
                    and relationships that drive the story forward.''',
            backstory='''You are a character psychologist and dialogue expert who 
                        understands what makes characters feel real and engaging. 
                        You've studied human behavior, personality types, and social 
                        dynamics. You excel at creating diverse characters with unique 
                        voices, motivations, and flaws that make them interesting. 
                        Every character you create feels like a real person with their 
                        own agenda and personality.''',
            verbose=True,
            allow_delegation=False,
            llm=llm
        )
    
    def create_character(self, character_type: str, story_context: str, 
                        personality_traits: List[str] = None) -> str:
        """
        Generate a new character with personality and background
        
        Args:
            character_type: Type of character (ally, enemy, merchant, etc.)
            story_context: Current story situation
            personality_traits: Optional specific traits to include
            
        Returns:
            Character description and personality profile
        """
        traits = personality_traits or ["determined", "curious", "cautious"]
        traits_str = ", ".join(traits)
        
        task_description = f"""
        Create a {character_type} character for an interactive fiction story.
        
        Story Context: {story_context}
        Suggested Personality Traits: {traits_str}
        
        Generate:
        - Name and brief physical description (1-2 sentences)
        - Personality summary (2-3 key traits with examples)
        - Current motivation or goal
        - A unique speaking pattern or mannerism
        - How they might react to the player character
        
        Make the character feel real and memorable, with clear motivations.
        """
        
        return task_description
    
    def generate_dialogue(self, character_name: str, character_personality: str,
                         situation: str, player_action: str = None) -> str:
        """
        Generate character dialogue based on personality and situation
        
        Args:
            character_name: Name of the speaking character
            character_personality: Brief personality description
            situation: Current story situation
            player_action: What the player just did (optional)
            
        Returns:
            Character dialogue appropriate to their personality
        """
        action_context = f"Player just: {player_action}" if player_action else ""
        
        task_description = f"""
        Generate dialogue for {character_name} in the current situation.
        
        Character Personality: {character_personality}
        Current Situation: {situation}
        {action_context}
        
        Requirements:
        - Stay true to the character's established personality
        - 1-3 sentences of dialogue
        - Include character-appropriate speech patterns
        - Advance the conversation or story
        - Provide potential response options for the player
        
        Format: Direct dialogue in quotes, plus brief action description if needed.
        """
        
        return task_description
    
    def manage_character_relationship(self, character_name: str, 
                                    relationship_status: str,
                                    recent_interactions: List[str]) -> str:
        """
        Update character relationship based on player interactions
        
        Args:
            character_name: Name of the character
            relationship_status: Current relationship state
            recent_interactions: List of recent player choices affecting this character
            
        Returns:
            Updated relationship description and character attitude
        """
        interactions_str = "; ".join(recent_interactions)
        
        task_description = f"""
        Update the relationship between the player and {character_name}.
        
        Current Relationship: {relationship_status}
        Recent Player Actions: {interactions_str}
        
        Determine:
        - How the character's attitude toward the player has changed
        - New relationship status (friendly, neutral, suspicious, hostile, etc.)
        - How this will affect future interactions
        - Any special dialogue or behavior changes
        
        Be realistic about how relationships evolve based on actions.
        """
        
        return task_description