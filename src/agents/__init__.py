"""
Interactive Fiction Engine - Agents Package

This package contains all the specialized AI agents for the interactive fiction system:
- WorldAgent: Creates and manages game world locations and environments
- CharacterAgent: Handles NPCs, dialogue, and character interactions
- StoryAgent: Manages plot progression and narrative choices
- CoordinatorAgent: Orchestrates agent collaboration and user interaction
"""

from .world_agent import create_world_builder_agent, create_world_building_task
from .character_agent import create_character_manager_agent, create_character_task
from .story_agent import create_story_director_agent, create_story_task
from .coordinator_agent import create_game_coordinator_agent, create_coordination_task

__all__ = [
    'create_world_builder_agent',
    'create_world_building_task',
    'create_character_manager_agent', 
    'create_character_task',
    'create_story_director_agent',
    'create_story_task',
    'create_game_coordinator_agent',
    'create_coordination_task'
]