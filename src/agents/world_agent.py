from crewai import Agent, Task
from crewai.tools import BaseTool
import json
from game_state import game_state

class CreateLocationTool(BaseTool):
    name: str = "create_location"
    description: str = "Create a new location in the game world. Pass JSON string with name, description, exits, and items"
    
    def _run(self, location_info: str) -> str:
        """Create a new location in the game world."""
        try:
            # Handle both string and already-parsed JSON
            if isinstance(location_info, str):
                # If it's a string, try to parse it as JSON
                try:
                    location_data = json.loads(location_info)
                except json.JSONDecodeError:
                    # If JSON parsing fails, treat as simple description
                    # Extract name from the beginning if it follows "name: description" format
                    if ":" in location_info:
                        parts = location_info.split(":", 1)
                        location_name = parts[0].strip()
                        description = parts[1].strip()
                    else:
                        location_name = "generated_starting_area"
                        description = location_info
                    
                    location_data = {
                        "name": location_name,
                        "description": description,
                        "exits": ["north", "east", "west"],  # Standard exits for starting area
                        "items": []
                    }
            else:
                location_data = location_info
                
            location_name = location_data.get("name", "unnamed_location")
            
            # CRITICAL: Save directly to game_state
            game_state.add_location(location_name, location_data)
            
            return f"✅ Successfully created location '{location_name}' in game_state"
        except Exception as e:
            return f"❌ Error creating location: {str(e)}"

class CreateStartingWorldTool(BaseTool):
    name: str = "create_starting_world"
    description: str = "Create a completely unique starting world for the adventure using creative LLM generation"
    
    def _run(self, world_theme: str = "fantasy_adventure") -> str:
        """Create a dynamic, unique starting world and save it to game_state"""
        try:
            import random
            
            # Generate unique themes for variety
            themes = [
                "mystical_forest_grove",
                "ancient_ruined_temple", 
                "floating_sky_island",
                "underground_crystal_cavern",
                "abandoned_wizard_tower",
                "enchanted_garden_maze",
                "misty_mountain_peak",
                "forgotten_library_vault",
                "magical_academy_courtyard",
                "mysterious_seaside_cliff",
                "ethereal_moonlit_glade",
                "crumbling_observatory_tower",
                "hidden_desert_oasis",
                "frozen_ice_palace_ruins"
            ]
            
            chosen_theme = random.choice(themes)
            
            # Create rich location templates with detailed descriptions and meaningful items
            location_templates = {
                "mystical_forest_grove": {
                    "name": "enchanted_grove",
                    "description": "You awaken in a mystical grove where ancient trees pulse with soft, ethereal light. Glowing mushrooms carpet the forest floor like fallen stars, and the air shimmers with magical particles that dance in lazy spirals. Strange, melodic whispers drift through the canopy above, as if the forest itself is singing secrets of ages past. The bark of the trees bears intricate spiral patterns that seem to shift when you're not looking directly at them.",
                    "exits": ["north", "east", "west"],
                    "items": [
                        {"name": "crystal_shard", "description": "A gleaming crystal shard that thrums with magical energy, warm to the touch and faintly humming"},
                        {"name": "ancient_rune_stone", "description": "A moss-covered stone etched with mysterious glowing runes that pulse in rhythm with your heartbeat"},
                        {"name": "sprite_lantern", "description": "A delicate lantern that seems to contain a tiny dancing light - perhaps a captured fairy or wisp"}
                    ]
                },
                "ancient_ruined_temple": {
                    "name": "crumbling_temple",
                    "description": "You stand in the ruins of an ancient temple, its once-grand pillars now weathered and vine-covered, reaching toward holes in the collapsed roof like stone fingers grasping at the sky. Shafts of golden sunlight pierce through the gaps, illuminating strange hieroglyphs that cover every surface. The air carries the lingering scent of incense and old mysteries, and you can almost hear the echoes of forgotten prayers in the rustling of leaves.",
                    "exits": ["north", "east", "west"],
                    "items": [
                        {"name": "ritual_dagger", "description": "An ornate ceremonial dagger with symbols that seem to shift and change in the light, its blade untarnished by time"},
                        {"name": "prayer_scroll", "description": "An ancient scroll written in flowing script of an unknown language, the parchment surprisingly supple"},
                        {"name": "golden_offering_bowl", "description": "A tarnished gold bowl that once held sacred offerings, still emanating a sense of reverence"}
                    ]
                },
                "floating_sky_island": {
                    "name": "floating_isle",
                    "description": "You find yourself on a floating island suspended impossibly in an endless expanse of sky. Wispy clouds drift lazily past at eye level, and far below, the world stretches out like a patchwork quilt of greens and browns. The wind carries the crisp scent of ozone and freedom, while above, strange sky-ships with billowing sails occasionally glide past in the distance like aerial whales. The edge of the island drops away into misty nothingness.",
                    "exits": ["north", "east", "west"],
                    "items": [
                        {"name": "wind_compass", "description": "A brass compass that points toward air currents instead of magnetic north, its needle dancing with the breeze"},
                        {"name": "cloud_essence", "description": "A crystal vial containing swirling, luminescent cloud matter that seems to defy gravity"},
                        {"name": "feathered_cloak", "description": "A magnificent cloak made from the iridescent feathers of sky-dwelling creatures, surprisingly light"}
                    ]
                },
                "underground_crystal_cavern": {
                    "name": "crystal_chambers",
                    "description": "You awaken in a vast underground cavern filled with towering crystal formations that stretch from floor to ceiling like a frozen forest. The crystals pulse with their own inner light, casting shifting rainbow patterns across the cavern walls in a mesmerizing display. The sound of dripping water echoes from somewhere in the distance, and you can feel the immense weight of the earth above pressing down, creating an atmosphere of ancient, geological patience.",
                    "exits": ["north", "east", "west"],
                    "items": [
                        {"name": "resonant_crystal", "description": "A musical crystal that chimes softly when touched, each note hanging in the air like a prayer"},
                        {"name": "miners_lantern", "description": "A well-used lantern left behind by previous explorers, still containing a few drops of oil"},
                        {"name": "gem_chisel", "description": "A precise tool for extracting precious stones, its edge still sharp and ready for use"}
                    ]
                },
                "abandoned_wizard_tower": {
                    "name": "wizards_sanctum",
                    "description": "You stand in the lower chamber of an abandoned wizard's tower, where dusty tomes line the walls from floor to vaulted ceiling, their leather bindings cracked with age. Magical apparatus sits covered in cobwebs - alchemical distilleries, star charts, and arcane instruments whose purposes are long forgotten. A spiral staircase winds upward into shadow, while strange symbols glow faintly on the stone floor beneath your feet, pulsing with residual magic.",
                    "exits": ["north", "east", "west"],
                    "items": [
                        {"name": "spell_component_pouch", "description": "A leather pouch containing various magical components: dried herbs, small gems, and powders that shimmer with potential"},
                        {"name": "enchanted_quill", "description": "A raven-black quill that writes by itself when dipped in magical ink, sometimes forming words you didn't intend"},
                        {"name": "scrying_orb", "description": "A cloudy crystal orb that occasionally shows distant visions - glimpses of other places and times"}
                    ]
                },
                "enchanted_garden_maze": {
                    "name": "living_maze",
                    "description": "You find yourself in an enchanted garden where hedges of luminous silver leaves form a living maze that seems to breathe and shift when you're not watching. Flowers of impossible colors bloom at your feet, their petals chiming like tiny bells in the breeze. The pathways are carpeted with soft moss that glows faintly green, and overhead, a canopy of intertwined branches filters dappled, ever-changing light. The air is sweet with the scent of nectar and growing things.",
                    "exits": ["north", "east", "west"],
                    "items": [
                        {"name": "singing_flower", "description": "A remarkable flower that hums melodious tunes when the wind passes through its crystalline petals"},
                        {"name": "maze_compass", "description": "A peculiar compass that points not north, but toward the heart of any labyrinth"},
                        {"name": "dewdrop_vial", "description": "A vial filled with morning dewdrops from enchanted roses, said to have healing properties"}
                    ]
                }
            }
            
            # Get the template or create a generic one if theme not found
            location_data = location_templates.get(chosen_theme, {
                "name": "mysterious_starting_place",
                "description": f"You find yourself in a {chosen_theme.replace('_', ' ')}, a place filled with wonder and possibilities. The air itself seems to hum with potential adventure, and every shadow holds the promise of discovery.",
                "exits": ["north", "east", "west"],
                "items": [
                    {"name": "mysterious_artifact", "description": "An intriguing object that pulses with unknown energy, its purpose shrouded in mystery"}
                ]
            })
            
            # CRITICAL: Add the location to the game state - this is the single source of truth
            game_state.add_location(location_data["name"], location_data)
            
            return f"✅ Created unique starting world '{location_data['name']}' in game_state with {len(location_data['items'])} items and {len(location_data['exits'])} exits"
            
        except Exception as e:
            return f"❌ Error creating starting world: {str(e)}"

class GetWorldStateTool(BaseTool):
    name: str = "get_world_state"
    description: str = "Get the current state of the game world including all locations"
    
    def _run(self) -> str:
        """Get current world state for context"""
        world_info = game_state.get_state()["world"]
        return json.dumps(world_info, indent=2)

class AddItemToLocationTool(BaseTool):
    name: str = "add_item_to_location"
    description: str = "Add an item to a specific location in the game world"
    
    def _run(self, item_info: str) -> str:
        """Add an item to a specific location."""
        try:
            # Handle both JSON and simple string input
            if isinstance(item_info, str):
                try:
                    data = json.loads(item_info)
                except json.JSONDecodeError:
                    # If not JSON, return error message
                    return "❌ Error: item_info must be JSON format like {\"location\": \"place\", \"item\": \"item_name\", \"description\": \"item description\"}"
            else:
                data = item_info
                
            location_name = data.get("location")
            item = data.get("item")
            description = data.get("description", "")
            
            # CRITICAL: Modify game_state directly
            state = game_state.get_state()
            locations = state["world"]["locations"]
            
            if location_name in locations:
                if "items" not in locations[location_name]:
                    locations[location_name]["items"] = []
                locations[location_name]["items"].append({
                    "name": item,
                    "description": description
                })
                game_state.log_event(f"Added item {item} to {location_name}")
                return f"✅ Added '{item}' to '{location_name}' in game_state"
            else:
                return f"❌ Location '{location_name}' does not exist in game_state"
        except Exception as e:
            return f"❌ Error adding item: {str(e)}"

class MovePlayerTool(BaseTool):
    name: str = "move_player"
    description: str = "Move the player to a new location"
    
    def _run(self, location_name: str) -> str:
        """Move player to a new location."""
        try:
            # CRITICAL: Update game_state directly
            game_state.set_current_location(location_name)
            return f"✅ Player moved to '{location_name}' in game_state"
        except Exception as e:
            return f"❌ Error moving player: {str(e)}"

class ConnectLocationsTool(BaseTool):
    name: str = "connect_locations"
    description: str = "Connect two locations by adding exits between them"
    
    def _run(self, connection_info: str) -> str:
        """Connect two locations with exits."""
        try:
            if isinstance(connection_info, str):
                try:
                    data = json.loads(connection_info)
                except json.JSONDecodeError:
                    return "❌ Error: connection_info must be JSON format like {\"from\": \"location1\", \"to\": \"location2\", \"direction\": \"north\"}"
            else:
                data = connection_info
            
            from_location = data.get("from")
            to_location = data.get("to")
            direction = data.get("direction")
            
            # Get the reverse direction
            reverse_directions = {
                "north": "south", "south": "north",
                "east": "west", "west": "east",
                "up": "down", "down": "up",
                "northeast": "southwest", "southwest": "northeast",
                "northwest": "southeast", "southeast": "northwest"
            }
            reverse_direction = reverse_directions.get(direction, "back")
            
            # CRITICAL: Modify game_state directly
            state = game_state.get_state()
            locations = state["world"]["locations"]
            
            # Add exit from first location to second
            if from_location in locations:
                if "exits" not in locations[from_location]:
                    locations[from_location]["exits"] = []
                if direction not in locations[from_location]["exits"]:
                    locations[from_location]["exits"].append(direction)
            
            # Add reverse exit from second location to first
            if to_location in locations:
                if "exits" not in locations[to_location]:
                    locations[to_location]["exits"] = []
                if reverse_direction not in locations[to_location]["exits"]:
                    locations[to_location]["exits"].append(reverse_direction)
            
            game_state.log_event(f"Connected {from_location} and {to_location}")
            return f"✅ Connected '{from_location}' to '{to_location}' via '{direction}' in game_state"
            
        except Exception as e:
            return f"❌ Error connecting locations: {str(e)}"

def create_world_builder_agent():
    """Create the World Agent with enhanced tools for dynamic world creation"""
    
    world_builder = Agent(
        role="Master World Builder & Environment Creator",
        goal="Create immersive, unique locations and manage dynamic world environments that inspire adventure",
        backstory="""You are a master world builder who creates rich, atmospheric environments 
        that spark imagination and adventure. You excel at generating unique, engaging locations
        with vivid descriptions, meaningful items, and logical connections that enhance the player's
        experience. You understand how environment tells story and creates mood.
        
        CRITICAL RESPONSIBILITY:
        - Your tools directly modify the game_state - this is the single source of truth
        - Every location, item, and connection you create is saved permanently to game_state
        - Other agents and the main application read from this same game_state for consistency
        - Never describe world elements that don't exist in game_state
        
        CREATIVE GUIDELINES:
        - Every location should feel unique and atmospheric with rich sensory details
        - Include environmental storytelling through descriptions and meaningful items
        - Create mysterious or intriguing elements that invite exploration
        - Ensure items are story-relevant and enhance the adventure experience
        - Make locations feel lived-in and authentic to their setting
        
        TOOL USAGE:
        - create_starting_world: Generate rich, themed starting locations automatically
        - create_location: Add new locations with detailed descriptions and items
        - add_item_to_location: Place meaningful items in specific locations
        - move_player: Update player position in the world
        - connect_locations: Create logical pathways between areas
        - get_world_state: Check current world state before making changes
        """,
        tools=[
            CreateLocationTool(),
            CreateStartingWorldTool(),
            GetWorldStateTool(),
            AddItemToLocationTool(),
            MovePlayerTool(),
            ConnectLocationsTool()
        ],
        verbose=True,
        allow_delegation=False
    )
    
    return world_builder

def create_world_building_task(user_input: str, specific_request: str = None):
    """Create a task for the World Agent"""
    
    request = specific_request or f"Handle world-building aspects of: {user_input}"
    
    task = Task(
        description=f"""
        {request}
        
        CRITICAL: All your actions modify the game_state directly through your tools.
        This game_state is the single source of truth that all other agents and the main application read from.
        
        Available tools that save directly to game_state:
        - create_starting_world: Generate completely unique starting worlds with themes and rich details
        - create_location: Create new locations with JSON format (name, description, exits, items)
        - get_world_state: Check current world state before making changes
        - add_item_to_location: Add items to locations with JSON format
        - move_player: Move player to new location in game_state
        - connect_locations: Create exits between locations
        
        CREATIVITY FOCUS:
        - Generate unique, atmospheric descriptions that create mood and intrigue
        - Include meaningful items that hint at adventure possibilities and story elements
        - Create environmental storytelling through rich details and atmosphere
        - Make every location feel distinct and memorable with sensory details
        - Add mysterious elements that invite exploration and discovery
        
        CONSISTENCY REQUIREMENT:
        - Always use tools to modify game_state rather than just describing changes
        - Verify changes with get_world_state if needed
        - Remember that your tool actions are permanent and will be read by other agents
        
        When creating locations, use proper JSON format with rich, evocative descriptions
        that make players excited to explore and discover what lies ahead.
        """,
        agent=create_world_builder_agent(),
        expected_output="Confirmation of world changes made to game_state with rich descriptions of new environments created"
    )
    
    return task