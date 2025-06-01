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
    
    def __init__(self, world_agent, character_agent, story_agent, image_agent=None, llm=None):
        self.world_agent = world_agent
        self.character_agent = character_agent  
        self.story_agent = story_agent
        self.image_agent = image_agent  # Add image agent
        
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
        self.current_theme = story_theme  # STORE THE THEME!
        self.game_state = {
            "turn": 0,
            "location": "starting_area",
            "characters_present": [],
            "inventory": [],
            "relationships": {},
            "plot_flags": {},
            "theme": story_theme  # STORE THEME IN GAME STATE
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
    
    def _get_theme_instructions(self, theme: str, choice: str) -> str:
        """
        Get theme-appropriate instructions for agents
        """
        
        theme_configs = {
            "fantasy_adventure": {
                "genre": "FANTASY ADVENTURE",
                "elements": "magic, swords, dragons, castles, wizards, medieval settings",
                "avoid": "modern technology, sci-fi elements"
            },
            "steampunk_adventure": {
                "genre": "STEAMPUNK ADVENTURE", 
                "elements": "steam, brass, gears, airships, Victorian technology, clockwork",
                "avoid": "fantasy magic, modern electronics"
            },
            "horror_survival": {
                "genre": "HORROR SURVIVAL",
                "elements": "darkness, fear, survival, psychological tension, monsters, abandoned places",
                "avoid": "comedy, bright cheerful settings"
            },
            "sci_fi_exploration": {
                "genre": "SCI-FI EXPLORATION",
                "elements": "space, technology, aliens, futuristic cities, starships, advanced science",
                "avoid": "medieval fantasy, steampunk"
            },
            "mystery_detective": {
                "genre": "MYSTERY DETECTIVE",
                "elements": "clues, investigation, suspects, crime scenes, deduction, noir atmosphere",
                "avoid": "action movie elements, fantasy magic"
            },
            "modern_thriller": {
                "genre": "MODERN THRILLER",
                "elements": "contemporary settings, espionage, chase scenes, modern technology, suspense",
                "avoid": "fantasy elements, historical settings"
            }
        }
        
        config = theme_configs.get(theme, theme_configs["fantasy_adventure"])
        
        return f"""
        CRITICAL: This is a {config['genre']} story. Maintain genre consistency!
        
        CURRENT SPECIFIC STORY CONTEXT:
        - Character: {self._get_current_character()}
        - Setting: {self._get_current_setting()}
        - Situation: {self._get_current_situation()}
        - Player Choice: {choice} 
        - What this choice means: {self._interpret_choice(choice)}
        
        RECENT STORY EVENTS:
        {self.story_history[-2:] if len(self.story_history) > 1 else ['Story just started']}
        
        COORDINATE WITH ALL AGENTS TO CONTINUE THIS SPECIFIC STORY:
        
        1. World Agent: Describe what happens in the current setting when player does: {choice}
           - Current location: {self._get_current_setting()}
           - Show the result of the player's action
           - Include: {config['elements']}
           - AVOID: {config['avoid']}
        
        2. Character Agent: Show how characters react to the player's choice: {choice}
           - Continue interactions with established characters
           - Show dialogue and reactions specific to this situation
        
        3. Story Agent: Advance the plot based on this specific choice: {choice}
           - Show immediate consequences of this action
           - Advance THIS specific storyline
           - Create new choices that follow logically from this situation
        
        SYNTHESIZE ALL INTO COHERENT {config['genre']} SCENE that directly follows from:
        Player choosing to: {choice}
        
        MAINTAIN STORY CONTINUITY - don't jump to different locations or situations!
        """
    
    def _get_current_character(self) -> str:
        """Extract current character from recent story"""
        # Look for character mentions in recent story
        recent = " ".join(self.story_history[-3:]) if self.story_history else ""
        if "Detective Alex Morgan" in recent:
            return "Detective Alex Morgan"
        elif "Emily" in recent:
            return "Emily"
        elif "Amelia Lockhart" in recent:
            return "Amelia Lockhart"
        return "the protagonist"
    
    def _get_current_setting(self) -> str:
        """Extract current setting from recent story"""
        recent = " ".join(self.story_history[-3:]).lower() if self.story_history else ""
        if "alley" in recent:
            return "dark alley"
        elif "asylum" in recent:
            return "abandoned asylum"
        elif "tavern" in recent:
            return "clockwork tavern"
        elif "ironspire" in recent:
            return "Ironspire city"
        return "current location"
    
    def _get_current_situation(self) -> str:
        """Extract current situation from recent story"""
        recent = " ".join(self.story_history[-3:]) if self.story_history else ""
        # Extract key situation elements
        return recent[-200:] if recent else "story beginning"
    
    def _interpret_choice(self, choice: str) -> str:
        """Interpret what the player's choice means in context"""
        choice_lower = choice.lower()
        if "stealth" in choice_lower or "sneak" in choice_lower or choice == "3":
            return "player is trying to approach quietly/secretly"
        elif "confront" in choice_lower or choice == "1":
            return "player is being direct/aggressive"
        elif "observe" in choice_lower or choice == "2":
            return "player is being cautious/watching"
        elif "investigate" in choice_lower:
            return "player is looking for clues/evidence"
        return f"player chose: {choice}"
    
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
        
        # Get theme information for consistency
        current_theme = getattr(self, 'current_theme', self.game_state.get('theme', 'unknown'))
        
        # Create theme-appropriate instructions
        theme_instructions = self._get_theme_instructions(current_theme, choice)
        
        # Create coordinated response using all agents
        coordination_task = Task(
            description=theme_instructions,
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
        
        # Generate image for this turn if image agent available
        if self.image_agent:
            try:
                print("🎨 Generating artistic image for this scene...")
                image_info = self.image_agent.create_scene_image(
                    story_content=str(result),
                    turn_number=self.game_state["turn"],
                    location=self.game_state.get("location", "unknown"),
                    characters_present=self.game_state.get("characters_present", []),
                    mood="mysterious"  # Could be extracted from story context
                )
                
                if image_info.get("success"):
                    print(f"✅ Image created: {image_info['filename']}")
                    self.game_state["last_image"] = image_info["filepath"]
                else:
                    print(f"⚠️ Image generation failed: {image_info.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"⚠️ Image generation error: {e}")
        
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