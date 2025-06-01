"""
Interactive Fiction Engine - Main Crew System
Brings together all agents for collaborative storytelling
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from agents import WorldAgent, CharacterAgent, StoryAgent, CoordinatorAgent

# Load environment variables
load_dotenv()


class InteractiveFictionCrew:
    """
    Main crew system that orchestrates all agents for interactive fiction creation
    """
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", temperature: float = 0.7):
        """
        Initialize the Interactive Fiction Crew
        
        Args:
            model_name: LLM model to use (gpt-3.5-turbo, gpt-4, etc.)
            temperature: Creativity level (0.0-1.0, higher = more creative)
        """
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Initialize all agents
        print("🌍 Initializing World Agent...")
        self.world_agent = WorldAgent(llm=self.llm)
        
        print("👥 Initializing Character Agent...")
        self.character_agent = CharacterAgent(llm=self.llm)
        
        print("📖 Initializing Story Agent...")
        self.story_agent = StoryAgent(llm=self.llm)
        
        print("🎯 Initializing Coordinator Agent...")
        self.coordinator_agent = CoordinatorAgent(
            world_agent=self.world_agent,
            character_agent=self.character_agent,
            story_agent=self.story_agent,
            llm=self.llm
        )
        
        print("✅ All agents initialized successfully!")
        
        # Story themes available
        self.available_themes = {
            "1": "fantasy_adventure",
            "2": "sci_fi_exploration", 
            "3": "mystery_detective",
            "4": "horror_survival",
            "5": "modern_thriller",
            "6": "steampunk_adventure"
        }
    
    def start_new_story(self, theme: str = None) -> str:
        """
        Start a new interactive fiction story
        
        Args:
            theme: Story theme/genre (optional, will prompt if not provided)
            
        Returns:
            Opening scene with initial choices
        """
        if not theme:
            theme = self._select_theme()
        
        print(f"\n🚀 Starting new {theme.replace('_', ' ').title()} story...")
        print("⚙️ Agents are collaborating to create your opening scene...\n")
        
        opening_scene = self.coordinator_agent.initialize_story(theme)
        return opening_scene
    
    def _select_theme(self) -> str:
        """Interactive theme selection"""
        print("\n🎨 Choose your story theme:")
        for key, theme in self.available_themes.items():
            print(f"  {key}. {theme.replace('_', ' ').title()}")
        
        while True:
            choice = input("\nEnter your choice (1-6): ").strip()
            if choice in self.available_themes:
                return self.available_themes[choice]
            print("❌ Invalid choice. Please enter a number 1-6.")
    
    def process_choice(self, choice: str) -> str:
        """
        Process a player choice and generate the next scene
        
        Args:
            choice: Player's choice/action
            
        Returns:
            Next scene description with new choices
        """
        print(f"\n⚙️ Processing your choice: {choice}")
        print("🤝 Agents are collaborating to create the next scene...\n")
        
        next_scene = self.coordinator_agent.process_player_choice(choice)
        return next_scene
    
    def get_story_status(self) -> dict:
        """Get current story status and statistics"""
        return self.coordinator_agent.get_game_state()
    
    def save_story(self, filename: str = None) -> bool:
        """Save current story progress"""
        if not filename:
            filename = f"story_save_{self.coordinator_agent.game_state['turn']}.json"
        
        success = self.coordinator_agent.save_game_state(filename)
        if success:
            print(f"💾 Story saved as {filename}")
        else:
            print("❌ Failed to save story")
        return success
    
    def load_story(self, filename: str) -> bool:
        """Load a previously saved story"""
        success = self.coordinator_agent.load_game_state(filename)
        if success:
            print(f"📂 Story loaded from {filename}")
        else:
            print("❌ Failed to load story")
        return success
    
    def get_story_summary(self) -> str:
        """Generate a summary of the story so far"""
        print("📝 Generating story summary...")
        return self.coordinator_agent.generate_story_summary()


# Utility functions for the interactive experience
def display_scene(scene_text: str):
    """Display a scene with nice formatting"""
    print("=" * 80)
    print(scene_text)
    print("=" * 80)


def get_player_input(prompt: str = "\n🎮 What do you choose? ") -> str:
    """Get player input with error handling"""
    while True:
        try:
            choice = input(prompt).strip()
            if choice:
                return choice
            print("❌ Please enter a valid choice.")
        except KeyboardInterrupt:
            print("\n👋 Thanks for playing!")
            return "quit"
        except Exception as e:
            print(f"❌ Input error: {e}")


def display_help():
    """Display help information"""
    help_text = """
    🎮 Interactive Fiction Engine - Help
    
    Commands:
    - Type your choice or action in natural language
    - 'help' - Show this help message
    - 'status' - Show current game status
    - 'summary' - Get a summary of the story so far
    - 'save' - Save your current progress
    - 'quit' - Exit the game
    
    Tips:
    - Be descriptive in your choices
    - Try different approaches to see how the story changes
    - Your choices matter and will affect the story!
    """
    print(help_text)


if __name__ == "__main__":
    # Example usage
    print("🎭 Interactive Fiction Engine - CrewAI Demo")
    print("=" * 50)
    
    try:
        # Initialize the crew
        crew = InteractiveFictionCrew()
        
        # Start a new story
        opening = crew.start_new_story()
        display_scene(opening)
        
        # Game loop
        while True:
            user_input = get_player_input()
            
            # Handle special commands
            if user_input.lower() == "quit":
                print("👋 Thanks for playing!")
                break
            elif user_input.lower() == "help":
                display_help()
                continue
            elif user_input.lower() == "status":
                status = crew.get_story_status()
                print(f"📊 Turn: {status['turn']}, Choices made: {status['choices_made']}")
                continue
            elif user_input.lower() == "summary":
                summary = crew.get_story_summary()
                print(f"📝 Story Summary:\n{summary}")
                continue
            elif user_input.lower() == "save":
                crew.save_story()
                continue
            
            # Process the choice
            next_scene = crew.process_choice(user_input)
            display_scene(next_scene)
            
    except KeyboardInterrupt:
        print("\n👋 Thanks for playing!")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Please check your API key and internet connection.")