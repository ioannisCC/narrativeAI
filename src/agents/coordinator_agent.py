"""
Coordinator Agent - Game Master & Flow Controller
Responsible for orchestrating all agents and managing game flow
"""

from crewai import Agent, Task, Crew
from typing import Dict, List, Any, Optional
import json


class CoordinatorAgent:
    """
    The Coordinator Agent acts as the Game Master, orchestrating collaboration
    between all other agents and managing the overall game flow and state.
    """
    
    def __init__(self, world_agent, character_agent, story_agent, llm=None):
        self.world_agent = world_agent
        self.character_agent = character_agent  
        self.story_agent = story_agent
        
        # Game state tracking
        self.story_history = []
        self.current_location = ""
        self.active_characters = {}
        self.player_choices = []
        self.game_state = {
            "turn": 0,
            "location": "",
            "characters_present": [],
            "inventory": [],
            "relationships": {},
            "plot_flags": {}
        }
        
        self.agent = Agent(
            role='Game Master & Narrative Coordinator',
            goal='''Orchestrate all agents to create a cohesive, engaging interactive 
                    fiction experience. Manage game flow, maintain story consistency, 
                    and ensure all player choices lead to meaningful outcomes.''',
            backstory='''You are an experienced Game Master who has run countless 
                        campaigns and interactive stories. You understand how to 
                        weave together environment, characters, and plot into a 
                        seamless experience. You're skilled at managing complex 
                        narratives, maintaining consistency, and ensuring that 
                        every player choice feels impactful. You know when to 
                        delegate to specialists and how to synthesize their 
                        contributions into a unified story.''',
            verbose=True,
            allow_delegation=True,
            llm=llm
        )
    
    def initialize_story(self, story_theme: str = "fantasy_adventure") -> str:
        """
        Initialize a new interactive fiction story
        
        Args:
            story_theme: Theme/genre for the story
            
        Returns:
            Opening scene description with initial choices
        """
        # Reset game state
        self.story_history = []
        self.player_choices = []
        self.game_state = {
            "turn": 0,
            "location": "starting_area",
            "characters_present": [],
            "inventory": [],
            "relationships": {},
            "plot_flags": {}
        }
        
        # Create initial story setup
        setup_task = Task(
            description=f"""
            Create an engaging opening scene for a {story_theme} interactive fiction story.
            
            Requirements:
            - Set up an intriguing situation that hooks the player
            - Establish the player character's basic situation
            - Create an initial challenge or opportunity
            - End with 3-4 meaningful choices for the player
            - Keep the opening focused and not overwhelming
            
            Include:
            - Brief character setup (who is the player?)
            - Initial setting description
            - The inciting incident or call to adventure
            - Clear choice options that lead to different paths
            
            Style: Engaging, clear, appropriate for interactive fiction
            """,
            agent=self.agent,
            expected_output="Complete opening scene with player choices"
        )
        
        crew = Crew(agents=[self.agent], tasks=[setup_task])
        result = crew.kickoff()
        
        # Store initial state
        self.story_history.append(f"Story initialized: {story_theme}")
        self.game_state["turn"] = 1
        
        return str(result)
    
    def process_player_choice(self, choice: str, choice_index: int = None) -> str:
        """
        Process a player choice through all agents and generate the next scene
        
        Args:
            choice: The player's choice description
            choice_index: Index of the choice if from a numbered list
            
        Returns:
            Complete next scene with new choices
        """
        # Record the choice
        self.player_choices.append(choice)
        self.game_state["turn"] += 1
        
        # Create coordinated response using all agents
        coordination_task = Task(
            description=f"""
            Process the player's choice and create the next scene in coordination 
            with all specialist agents.
            
            Player Choice: {choice}
            Current Story State: {self.game_state}
            Recent History: {self.story_history[-3:] if self.story_history else []}
            
            Coordinate with:
            1. World Agent: Get environmental description and location features
            2. Character Agent: Handle any character interactions or introductions  
            3. Story Agent: Advance plot and create meaningful consequences
            
            Synthesize all contributions into:
            - Environmental description (from World Agent)
            - Character interactions (from Character Agent) 
            - Plot progression (from Story Agent)
            - 3-4 new meaningful choices for the player
            
            Ensure the scene flows naturally and player choice has clear impact.
            Maintain story consistency and build toward interesting developments.
            """,
            agent=self.agent,
            expected_output="Complete scene description with new player choices"
        )
        
        # Execute the coordinated response
        crew = Crew(
            agents=[
                self.agent,
                self.world_agent.agent,
                self.character_agent.agent, 
                self.story_agent.agent
            ],
            tasks=[coordination_task]
        )
        
        result = crew.kickoff()
        
        # Update story history
        self.story_history.append(f"Player chose: {choice}")
        self.story_history.append(f"Result: {str(result)[:100]}...")
        
        return str(result)
    
    def get_game_state(self) -> Dict[str, Any]:
        """Return current game state information"""
        return {
            "turn": self.game_state["turn"],
            "location": self.game_state["location"],
            "story_length": len(self.story_history),
            "choices_made": len(self.player_choices),
            "active_characters": len(self.game_state.get("characters_present", [])),
            "last_choice": self.player_choices[-1] if self.player_choices else None
        }
    
    def save_game_state(self, filename: str) -> bool:
        """Save current game state to file"""
        try:
            save_data = {
                "story_history": self.story_history,
                "player_choices": self.player_choices,
                "game_state": self.game_state,
                "current_location": self.current_location,
                "active_characters": self.active_characters
            }
            with open(filename, 'w') as f:
                json.dump(save_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Save failed: {e}")
            return False
    
    def load_game_state(self, filename: str) -> bool:
        """Load game state from file"""
        try:
            with open(filename, 'r') as f:
                save_data = json.load(f)
            
            self.story_history = save_data.get("story_history", [])
            self.player_choices = save_data.get("player_choices", [])
            self.game_state = save_data.get("game_state", {})
            self.current_location = save_data.get("current_location", "")
            self.active_characters = save_data.get("active_characters", {})
            
            return True
        except Exception as e:
            print(f"Load failed: {e}")
            return False
    
    def generate_story_summary(self) -> str:
        """Generate a summary of the story so far"""
        summary_task = Task(
            description=f"""
            Create a summary of the interactive fiction story so far.
            
            Story History: {self.story_history}
            Player Choices: {self.player_choices}
            Current State: {self.game_state}
            
            Generate:
            - Brief overview of the story progression
            - Key player decisions and their consequences
            - Current situation and character relationships
            - Major plot developments
            
            Keep it concise but capture the essence of the adventure.
            """,
            agent=self.agent,
            expected_output="Concise story summary"
        )
        
        crew = Crew(agents=[self.agent], tasks=[summary_task])
        result = crew.kickoff()
        
        return str(result)