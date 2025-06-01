"""
World Agent - Environmental Designer & Setting Creator
Responsible for creating immersive worlds and environments
"""

from crewai import Agent
from typing import Dict, Any


class WorldAgent:
    """
    The World Agent creates detailed environments, settings, and atmospheres
    for the interactive fiction story. This agent focuses on the physical
    world, ambiance, and environmental storytelling.
    """
    
    def __init__(self, llm=None):
        self.agent = Agent(
            role='Environmental Designer & World Builder',
            goal='''Create immersive, detailed environments and settings that enhance 
                    the interactive fiction experience. Focus on atmosphere, mood, 
                    physical descriptions, and world-building elements.''',
            backstory='''You are a master world-builder with an eye for detail and 
                        atmosphere. You've spent years crafting immersive environments 
                        for stories, from mystical forests to futuristic cities. 
                        You understand how environment shapes narrative and emotion. 
                        Your descriptions are vivid but not overwhelming, setting the 
                        perfect stage for adventure.''',
            verbose=True,
            allow_delegation=False,
            llm=llm
        )
    
    def create_environment_description(self, location_type: str, mood: str, 
                                     story_context: str) -> str:
        """
        Generate a detailed environment description based on the current story state
        
        Args:
            location_type: Type of location (forest, castle, city, etc.)
            mood: Desired emotional atmosphere (mysterious, cheerful, ominous, etc.)
            story_context: Current story situation for context
            
        Returns:
            Detailed environment description
        """
        task_description = f"""
        Create a vivid, atmospheric description of a {location_type} with a {mood} mood.
        
        Story Context: {story_context}
        
        Requirements:
        - 2-3 sentences maximum 
        - Focus on sensory details (sight, sound, smell, touch)
        - Create atmosphere that matches the {mood} mood
        - Leave room for character interaction and plot development
        - Avoid mentioning specific characters or plot elements
        
        Style: Engaging, immersive, appropriate for interactive fiction
        """
        
        return task_description
    
    def get_location_features(self, location_type: str) -> Dict[str, Any]:
        """
        Generate interactive features and elements for a location
        
        Args:
            location_type: Type of location to generate features for
            
        Returns:
            Dictionary of location features and interactive elements
        """
        task_description = f"""
        Generate interactive features and elements for a {location_type}.
        
        Provide a JSON-like structure with:
        - "interactive_objects": List of 3-4 objects players can interact with
        - "hidden_secrets": 1-2 hidden elements that might be discovered
        - "atmosphere_details": Environmental sounds, lighting, weather
        - "navigation_options": Possible directions or paths available
        
        Focus on elements that could lead to interesting story choices.
        """
        
        return task_description