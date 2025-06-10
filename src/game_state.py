from typing import Dict, List, Any
import json
import logging
import sys
from datetime import datetime

class TeeLogger:
    """Custom logger that writes to both console and file"""
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, 'a', encoding='utf-8')
        
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()
        
    def flush(self):
        self.terminal.flush()
        self.log.flush()
        
    def close(self):
        self.log.close()

# Setup comprehensive logging - capture EVERYTHING
log_filename = f"game_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# Redirect stdout to capture all terminal output
sys.stdout = TeeLogger(log_filename)

# Also setup standard logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename, mode='a'),
        logging.StreamHandler(sys.__stdout__)  # Use original stdout
    ]
)

print(f"=== GAME SESSION STARTED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
print(f"📝 All terminal output will be logged to: {log_filename}")

class GameState:
    """Shared game state that all agents can read and modify"""
    
    def __init__(self):
        self.state = {
            "player": {
                "name": "",
                "location": "starting_room",
                "inventory": [],
                "health": 100,
                "experience": 0
            },
            "world": {
                "locations": {},
                "current_location": "starting_room"
            },
            "characters": {},
            "story": {
                "current_chapter": 1,
                "events": [],
                "choices_made": []
            },
            "game_log": [],
            "turn_counter": {
                "current_turn": 0,
                "max_turns": 5,
                "game_ended": False
            }
        }
        self.session_start = datetime.now()
        self.log_filename = log_filename
        logging.info("=== NEW GAME SESSION STARTED ===")
        logging.info(f"Game configured for {self.state['turn_counter']['max_turns']} turns")
    
    def get_state(self) -> Dict[str, Any]:
        """Get current game state"""
        return self.state
    
    def update_player(self, updates: Dict[str, Any]):
        """Update player information"""
        self.state["player"].update(updates)
        log_msg = f"Player updated: {updates}"
        self.log_event(log_msg)
        logging.info(f"PLAYER_UPDATE: {updates}")
    
    def add_location(self, location_name: str, location_data: Dict[str, Any]):
        """Add a new location to the world"""
        self.state["world"]["locations"][location_name] = location_data
        log_msg = f"Location added: {location_name}"
        self.log_event(log_msg)
        logging.info(f"LOCATION_CREATED: {location_name} - {location_data.get('description', '')[:100]}...")
    
    def set_current_location(self, location_name: str):
        """Change player's current location"""
        old_location = self.state["player"]["location"]
        self.state["player"]["location"] = location_name
        self.state["world"]["current_location"] = location_name
        log_msg = f"Player moved from {old_location} to {location_name}"
        self.log_event(log_msg)
        logging.info(f"PLAYER_MOVEMENT: {old_location} -> {location_name}")
    
    def add_character(self, character_name: str, character_data: Dict[str, Any]):
        """Add a character to the game"""
        self.state["characters"][character_name] = character_data
        log_msg = f"Character added: {character_name}"
        self.log_event(log_msg)
        logging.info(f"CHARACTER_CREATED: {character_name} in {character_data.get('location', 'unknown')}")
    
    def add_story_event(self, event: str):
        """Add an event to the story log"""
        self.state["story"]["events"].append(event)
        log_msg = f"Story event: {event}"
        self.log_event(log_msg)
        logging.info(f"STORY_EVENT: {event}")
    
    def add_choice_made(self, choice: str):
        """Record a choice made by the player"""
        self.state["story"]["choices_made"].append(choice)
        log_msg = f"Choice made: {choice}"
        self.log_event(log_msg)
        logging.info(f"PLAYER_CHOICE: {choice}")
    
    def log_event(self, event: str):
        """Log any game event"""
        timestamped_event = f"[{datetime.now().strftime('%H:%M:%S')}] {event}"
        self.state["game_log"].append(timestamped_event)
    
    def increment_turn(self):
        """Increment the turn counter and check for game end"""
        self.state["turn_counter"]["current_turn"] += 1
        current = self.state["turn_counter"]["current_turn"]
        max_turns = self.state["turn_counter"]["max_turns"]
        
        logging.info(f"TURN_INCREMENT: Turn {current}/{max_turns}")
        self.log_event(f"Turn {current} begins")
        
        # Check if game should end
        if current >= max_turns:
            self.state["turn_counter"]["game_ended"] = True
            logging.info("GAME_END: Maximum turns reached")
            self.log_event("Game reaches its conclusion")
    
    def get_turn_info(self) -> dict:
        """Get turn information and progress"""
        turn_data = self.state["turn_counter"]
        progress = turn_data["current_turn"] / turn_data["max_turns"]
        
        if progress <= 0.2:
            phase = "beginning"
        elif progress <= 0.6:
            phase = "middle"
        elif progress <= 0.8:
            phase = "late"
        else:
            phase = "climax"
            
        return {
            "current_turn": turn_data["current_turn"],
            "max_turns": turn_data["max_turns"],
            "turns_remaining": turn_data["max_turns"] - turn_data["current_turn"],
            "progress": progress,
            "phase": phase,
            "game_ended": turn_data["game_ended"]
        }
    
    def is_game_ended(self) -> bool:
        """Check if the game has ended"""
        return self.state["turn_counter"]["game_ended"]
    
    def get_current_location_info(self) -> Dict[str, Any]:
        """Get information about current location"""
        current_loc = self.state["player"]["location"]
        return self.state["world"]["locations"].get(current_loc, {})
    
    def get_story_summary_data(self) -> Dict[str, Any]:
        """Get comprehensive data for story summarization"""
        session_duration = datetime.now() - self.session_start
        turn_info = self.get_turn_info()
        
        return {
            "session_info": {
                "duration_minutes": int(session_duration.total_seconds() / 60),
                "start_time": self.session_start.strftime('%Y-%m-%d %H:%M:%S'),
                "log_file": self.log_filename
            },
            "turn_info": turn_info,
            "player": self.state["player"],
            "locations_visited": list(self.state["world"]["locations"].keys()),
            "characters_met": list(self.state["characters"].keys()),
            "story_events": self.state["story"]["events"],
            "choices_made": self.state["story"]["choices_made"],
            "current_chapter": self.state["story"]["current_chapter"],
            "game_log": self.state["game_log"][-20:]  # Last 20 events
        }
    
    def close_logging(self):
        """Close the logging system"""
        try:
            print(f"\n=== GAME SESSION ENDED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
            print(f"📝 Complete session log saved to: {self.log_filename}")
            if hasattr(sys.stdout, 'close'):
                sys.stdout.close()
            sys.stdout = sys.__stdout__  # Restore original stdout
        except:
            pass
    
    def to_json(self) -> str:
        """Convert state to JSON for agent communication"""
        return json.dumps(self.state, indent=2)

# Global game state instance
game_state = GameState()