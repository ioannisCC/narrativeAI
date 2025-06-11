from crewai import Crew, Process
import os
import json
from dotenv import load_dotenv

load_dotenv()

IMPORTS_SUCCESSFUL = True
import_errors = []

try:
    from game_state import game_state
    print("✅ game_state imported successfully")
except ImportError as e:
    print(f"❌ game_state import failed: {e}")
    import_errors.append(f"game_state: {e}")
    IMPORTS_SUCCESSFUL = False

try:
    from agents.coordinator_agent import create_game_coordinator_agent, create_coordination_task
    print("✅ coordinator_agent imported successfully")
except ImportError as e:
    print(f"❌ coordinator_agent import failed: {e}")
    import_errors.append(f"coordinator_agent: {e}")
    IMPORTS_SUCCESSFUL = False

try:
    from agents.world_agent import create_world_builder_agent, create_world_building_task
    print("✅ world_agent imported successfully")
except ImportError as e:
    print(f"❌ world_agent import failed: {e}")
    import_errors.append(f"world_agent: {e}")
    IMPORTS_SUCCESSFUL = False

try:
    from agents.character_agent import create_character_manager_agent, create_character_task
    print("✅ character_agent imported successfully")
except ImportError as e:
    print(f"❌ character_agent import failed: {e}")
    import_errors.append(f"character_agent: {e}")
    IMPORTS_SUCCESSFUL = False

try:
    from agents.story_agent import create_story_director_agent, create_story_task
    print("✅ story_agent imported successfully")
except ImportError as e:
    print(f"❌ story_agent import failed: {e}")
    import_errors.append(f"story_agent: {e}")
    IMPORTS_SUCCESSFUL = False

if import_errors:
    print(f"\n❌ Import errors found:")
    for error in import_errors:
        print(f"   - {error}")
    print("\nPlease fix the import errors before continuing.")

class InteractiveFictionCrew:
    """Main crew class with intelligent agent selection and character continuity"""
    
    def __init__(self):
        """Initialize the crew with all agents and generate starting world"""
        if not IMPORTS_SUCCESSFUL:
            raise ImportError("Failed to import required agent modules")
            
        # Create all agents (available for intelligent delegation)
        try:
            print("🎯 Initializing intelligent multi-agent crew...")
            self.coordinator_agent = create_game_coordinator_agent()
            self.world_agent = create_world_builder_agent()
            self.character_agent = create_character_manager_agent()
            self.story_agent = create_story_director_agent()
            
            print("🌍 All agents created successfully. Generating dynamic starting world...")
            # Generate dynamic starting world using World Agent
            self._generate_dynamic_starting_world()
            
        except Exception as e:
            print(f"❌ Error creating agents: {e}")
            raise
    
    def _generate_dynamic_starting_world(self):
        """
        Generate starting world using World Agent tools, then read from game_state
        This prevents the "confabulation" issue by using single source of truth
        """
        print("🌍 Generating new adventure world with AI...")
        
        try:
            # Create a task for the World Builder to generate a unique starting scenario
            world_creation_task = create_world_building_task(
                "create starting world",
                """Create a completely unique and engaging starting location for an interactive fiction adventure.
                
                REQUIREMENTS:
                - Use the `create_starting_world` tool to generate a unique, themed starting location.
                - The tool will automatically handle the creation of the description, items, and exits.
                - Your only job is to call the tool to initiate the world creation process.
                """
            )
            
            # Use World Builder agent to create the starting world
            world_crew = Crew(
                agents=[self.world_agent],
                tasks=[world_creation_task],
                process=Process.sequential,
                verbose=False 
            )
            
            # Agent modifies game_state through tools, we ignore its Final Answer
            agent_result = world_crew.kickoff()  # Agent uses tools to save to game_state
            
            # Get the ground truth from game_state (single source of truth)
            # This ensures consistency with what the main game loop will display
            true_world_description = self.get_current_scene_description()
            
            print("\n✅ Dynamic starting world created:")
            print(true_world_description)
            
            game_state.add_story_event("A new adventure begins in a uniquely generated world")
            
        except Exception as e:
            print(f"❌ Error generating dynamic world: {e}")
            print("🔄 Falling back to minimal starting area...")
            
            # Fallback: create minimal starting area if LLM generation fails
            fallback_location = {
                "name": "mysterious_starting_area",
                "description": "You find yourself in an unknown place, ready to begin your adventure.",
                "exits": ["north", "east", "west"],
                "items": []
            }
            game_state.add_location("mysterious_starting_area", fallback_location)
            game_state.add_story_event("Adventure begins in a mysterious place")
    
    def _analyze_user_intent(self, user_input: str) -> dict:
        """Analyze what type of interaction the user wants - INTELLIGENT DELEGATION"""
        user_lower = user_input.lower()
        
        # Get current scene context from game_state
        state = game_state.get_state()
        current_location = state["player"]["location"]
        location_info = state["world"]["locations"].get(current_location, {})
        
        # Check for characters in current location - character continuity
        characters_present = []
        for char_name, char_data in state["characters"].items():
            if char_data.get("location") == current_location:
                characters_present.append(char_name)
        
        # Analyze intent across multiple dimensions
        intent = {
            "character_interaction": False,
            "world_building": False,
            "story_progression": False,
            "simple_coordination": False,
            "characters_present": characters_present
        }
        
        # 1. CHARACTER INTERACTION DETECTION
        character_keywords = ['ask', 'talk', 'speak', 'say', 'tell', 'greet', 'question', 'dialogue', 'chat']
        character_references = ['zephyr', 'npc', 'character', 'him', 'her', 'they', 'wizard', 'entity']
        choice_about_character = any(keyword in user_lower for keyword in ['option 1', 'choice 1']) and characters_present
        
        if (any(keyword in user_lower for keyword in character_keywords) or
            any(ref in user_lower for ref in character_references) or
            choice_about_character or
            characters_present):  # Characters are present in scene
            intent["character_interaction"] = True
        
        # 2. WORLD BUILDING DETECTION  
        world_keywords = ['go', 'move', 'travel', 'explore', 'enter', 'exit', 'north', 'south', 'east', 'west']
        creation_keywords = ['create', 'build', 'generate', 'new location']
        
        if (any(keyword in user_lower for keyword in world_keywords) or
            any(keyword in user_lower for keyword in creation_keywords)):
            intent["world_building"] = True
        
        # 3. STORY PROGRESSION DETECTION
        story_keywords = ['choose', 'option', 'decision', 'continue', 'next', 'progress']
        narrative_keywords = ['story', 'plot', 'what happens', 'then', 'enlightenment', 'quest']
        
        if (any(keyword in user_lower for keyword in story_keywords) or
            any(keyword in user_lower for keyword in narrative_keywords)):
            intent["story_progression"] = True
        
        # 4. SIMPLE COORDINATION (status, help, etc.)
        simple_keywords = ['status', 'help', 'look', 'examine', 'inventory', 'stats']
        
        if any(keyword in user_lower for keyword in simple_keywords):
            intent["simple_coordination"] = True
            
        return intent
    
    def _determine_agent_crew(self, user_input: str) -> tuple:
        """Determine which agents should handle this request - INTELLIGENT ROUTING"""
        intent = self._analyze_user_intent(user_input)
        turn_info = game_state.get_turn_info()
        
        # PRIORITY 1: CHARACTER INTERACTIONS
        if intent["character_interaction"]:
            print("👥 Activating Character Agent for NPC interaction...")
            agents = [self.coordinator_agent, self.character_agent]
            
            # Add Story Agent if this is a complex narrative moment
            if turn_info['current_turn'] > 2 or any(word in user_input.lower() for word in ['choose', 'option', 'enlightenment']):
                agents.append(self.story_agent)
                print("🎭 Adding Story Agent for enhanced character narrative...")
                
            return agents, "character_focused"
        
        # PRIORITY 2: WORLD BUILDING NEEDS
        elif intent["world_building"]:
            print("🏗️ Activating World Agent for environment creation...")
            agents = [self.coordinator_agent, self.world_agent]
            
            # Add Story Agent for rich world descriptions
            if turn_info['phase'] in ['middle', 'late', 'climax']:
                agents.append(self.story_agent)
                print("🎭 Adding Story Agent for atmospheric world building...")
                
            return agents, "world_focused"
        
        # PRIORITY 3: STORY PROGRESSION  
        elif intent["story_progression"]:
            print("🎭 Activating Story Agent for narrative development...")
            agents = [self.coordinator_agent, self.story_agent]
            
            # Add Character Agent if characters are present
            if intent["characters_present"]:
                agents.append(self.character_agent)
                print("👥 Adding Character Agent for character involvement...")
                
            return agents, "story_focused"
        
        # PRIORITY 4: SIMPLE COORDINATION
        elif intent["simple_coordination"]:
            print("⚡ Using Coordinator for quick response...")
            return [self.coordinator_agent], "simple"
        
        # DEFAULT: INTELLIGENT MULTI-AGENT FOR COMPLEX REQUESTS
        else:
            print("🎯 Using intelligent multi-agent approach...")
            agents = [self.coordinator_agent]
            
            # Add Story Agent for rich content after turn 1
            if turn_info['current_turn'] > 1:
                agents.append(self.story_agent)
                
            # Add Character Agent if characters present
            if intent["characters_present"]:
                agents.append(self.character_agent)
                print("👥 Including Character Agent due to characters present...")
                
            return agents, "multi_agent"
    
    def process_user_input(self, user_input: str) -> str:
        """ENHANCED: Process user input with intelligent agent selection and character continuity"""
        
        try:
            # Determine optimal agent crew for this specific request
            agents, crew_type = self._determine_agent_crew(user_input)
            
            print(f"🎯 Selected crew type: {crew_type} with {len(agents)} agents")
            
            # Create tasks based on crew type
            if crew_type == "character_focused":
                # CHARACTER-FOCUSED: Character Agent leads, Story Agent enhances
                coord_task = create_coordination_task(user_input)
                char_task = create_character_task(
                    user_input,
                    f"Handle character interaction for: '{user_input}' - maintain character continuity and generate appropriate dialogue responses"
                )
                tasks = [coord_task, char_task]
                
                # Add story task if story agent included
                if self.story_agent in agents:
                    story_task = create_story_task(
                        user_input,
                        f"Enhance character narrative for: '{user_input}' - support character interactions with rich storytelling"
                    )
                    tasks.append(story_task)
                    
            elif crew_type == "world_focused":
                # WORLD-FOCUSED: World Agent leads, Story Agent enhances
                coord_task = create_coordination_task(user_input)
                world_task = create_world_building_task(
                    user_input,
                    f"Handle world building for: '{user_input}' - create or modify locations as needed"
                )
                tasks = [coord_task, world_task]
                
                # Add story task if story agent included
                if self.story_agent in agents:
                    story_task = create_story_task(
                        user_input,
                        f"Add atmospheric storytelling for: '{user_input}' - enhance world descriptions with narrative elements"
                    )
                    tasks.append(story_task)
                    
            elif crew_type == "story_focused":
                # STORY-FOCUSED: Story Agent leads, Character Agent supports
                coord_task = create_coordination_task(user_input)
                story_task = create_story_task(
                    user_input,
                    f"Handle story progression for: '{user_input}' - advance narrative and provide meaningful choices"
                )
                tasks = [coord_task, story_task]
                
                # Add character task if character agent included
                if self.character_agent in agents:
                    char_task = create_character_task(
                        user_input,
                        f"Handle character aspects for: '{user_input}' - ensure character continuity and appropriate responses"
                    )
                    tasks.append(char_task)
                    
            else:  # simple or multi_agent
                # COORDINATION-FOCUSED: Coordinator leads with support as needed
                coord_task = create_coordination_task(user_input)
                tasks = [coord_task]
                
                # Add additional tasks for multi-agent approach
                if len(agents) > 1:
                    if self.story_agent in agents:
                        story_task = create_story_task(
                            user_input,
                            f"Enhance narrative for: '{user_input}' - add rich storytelling elements"
                        )
                        tasks.append(story_task)
                    if self.character_agent in agents:
                        char_task = create_character_task(
                            user_input,
                            f"Handle character elements for: '{user_input}' - maintain character presence and interactions"
                        )
                        tasks.append(char_task)
            
            # Create and run the intelligent crew
            crew = Crew(
                agents=agents,
                tasks=tasks,
                process=Process.sequential,
                verbose=False
            )
            
            result = crew.kickoff()
            return self._format_result(result)
            
        except Exception as e:
            return f"An error occurred while processing your input: {str(e)}"
    
    def _format_result(self, result) -> str:
        """Format the crew result into a readable string"""
        if hasattr(result, 'raw'):
            return str(result.raw)
        else:
            return str(result)
    
    def get_game_status(self) -> dict:
        """Get current game status from game_state"""
        return game_state.get_state()
    
    def get_current_scene_description(self) -> str:
        """
        CRITICAL: Get scene description from game_state (single source of truth)
        This ensures consistency across all game components
        """
        state = game_state.get_state()
        current_location = state["player"]["location"]
        
        # Handle case where location might not be set yet during initialization
        if not current_location:
             # Find the first location in the world dictionary
            if state["world"]["locations"]:
                current_location = list(state["world"]["locations"].keys())[0]
                # Update the player location to the first available location
                game_state.set_current_location(current_location)
            else:
                return "Error: No locations have been created in the world."

        location_info = state["world"]["locations"].get(current_location, {})
        
        description = f"\n--- {current_location.replace('_', ' ').title()} ---\n"
        description += location_info.get("description", "You are in an unknown place") + "\n"
        
        # Add items from game_state
        items = location_info.get("items", [])
        if items:
            description += "\nItems here:\n"
            for item in items:
                if isinstance(item, dict):
                    description += f"  - {item['name']}: {item.get('description', '')}\n"
                else:
                    description += f"  - {item}\n"
        
        # Add exits from game_state
        exits = location_info.get("exits", [])
        if exits:
            description += f"\nExits: {', '.join(exits)}\n"
        
        # Add characters from game_state
        characters_here = []
        for char_name, char_data in state["characters"].items():
            if char_data.get("location") == current_location:
                characters_here.append(char_name)
        
        if characters_here:
            description += f"\nCharacters here: {', '.join(characters_here)}\n"
        
        return description
    
    def debug_current_state(self):
        """Debug function to check current game state"""
        print("\n=== DEBUG: CURRENT GAME STATE ===")
        state = game_state.get_state()
        print(f"Current location: {state['player']['location']}")
        print(f"Total locations: {len(state['world']['locations'])}")
        print(f"Total characters: {len(state['characters'])}")
        
        # Show characters and their locations
        for char_name, char_data in state['characters'].items():
            print(f"Character: {char_name} at {char_data.get('location', 'unknown')}")
        
        print("=== END DEBUG ===\n")

# Create global crew instance with error handling and intelligent agent selection
if IMPORTS_SUCCESSFUL:
    try:
        fiction_crew = InteractiveFictionCrew()
        print("✅ Enhanced fiction crew with intelligent agent selection and character continuity initialized successfully")
        print("🎯 Ready for character interactions, world building, and story progression!")
    except Exception as e:
        print(f"❌ Error initializing fiction crew: {e}")
        print("Please check that all agent files are properly updated.")
        fiction_crew = None
else:
    fiction_crew = None
    print("❌ Cannot create fiction_crew due to import errors")