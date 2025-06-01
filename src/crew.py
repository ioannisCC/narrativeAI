"""
Updated crew.py - Using CrewAI's Built-in Memory System
Much simpler than custom Memory Agent!
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from crewai import Crew, Process

from agents import WorldAgent, CharacterAgent, StoryAgent, CoordinatorAgent, ImageAgent

# Load environment variables
load_dotenv()


class InteractiveFictionCrew:
    """
    Main crew system with built-in CrewAI memory for consistency
    """
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", temperature: float = 0.7):
        """
        Initialize the Interactive Fiction Crew with built-in memory
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
        
        print("🎨 Initializing Image Agent...")
        self.image_agent = ImageAgent(llm=self.llm)
        
        print("🎯 Initializing Coordinator Agent...")
        self.coordinator_agent = CoordinatorAgent(
            world_agent=self.world_agent,
            character_agent=self.character_agent,
            story_agent=self.story_agent,
            image_agent=self.image_agent,
            llm=self.llm
        )
        
        # Create the crew with BUILT-IN MEMORY enabled
        print("🧠 Creating crew with built-in memory system...")
        self.crew = Crew(
            agents=[
                self.coordinator_agent.agent,
                self.world_agent.agent,
                self.character_agent.agent,
                self.story_agent.agent
            ],
            process=Process.sequential,
            memory=True,  # 🔑 Enable built-in memory!
            verbose=True,
            # Optional: Configure memory for better performance
            memory_config={
                "provider": "mem0",  # Advanced memory provider
                "config": {
                    "user_id": "interactive_fiction_player",  # Track per-player
                    "local_mem0_config": {
                        "vector_store": {
                            "provider": "chroma",  # Use ChromaDB for storage
                        },
                        "llm": {
                            "provider": "openai",
                            "config": {
                                "api_key": os.getenv("OPENAI_API_KEY"),
                                "model": "gpt-3.5-turbo"
                            }
                        }
                    }
                }
            }
        )
        
        print("✅ All agents initialized with memory!")
        
        # Story state
        self.current_theme = None
        self.turn_count = 0
        self.max_turns = 5
        self.story_context = {
            "protagonist": "",
            "setting": "",
            "current_situation": "",
            "plot_threads": []
        }
    
    def start_new_story(self, theme: str = None) -> str:
        """
        Start a new interactive fiction story with memory tracking
        """
        if not theme:
            theme = self._select_theme()
        
        self.current_theme = theme
        self.turn_count = 0
        
        print(f"\n🚀 Starting new {theme.replace('_', ' ').title()} story...")
        print("🧠 Crew memory system is tracking story consistency...\n")
        
        # Create initialization task
        from crewai import Task
        
        init_task = Task(
            description=f"""
            Create an engaging opening scene for a {theme} interactive fiction story.
            
            This is the FIRST scene - establish the foundation that will be remembered.
            
            IMPORTANT: The crew's memory system will remember:
            - Character names and details
            - Setting descriptions 
            - Plot elements and conflicts
            - Story atmosphere and tone
            
            Requirements:
            - Set up an intriguing situation that hooks the player
            - Establish the player character's basic situation (name, role, background)
            - Create an initial challenge or opportunity
            - End with 3-4 meaningful numbered choices
            - Keep the opening focused and memorable
            
            Include:
            - Brief character setup (who is the player?)
            - Initial setting description 
            - The inciting incident or call to adventure
            - Clear choice options that lead to different paths
            
            Style: Engaging, clear, appropriate for {theme} genre.
            
            REMEMBER: This opening will be stored in memory for consistency!
            """,
            agent=self.coordinator_agent.agent,
            expected_output="Complete opening scene with numbered player choices"
        )
        
        # Execute with memory-enabled crew
        result = self.crew.kickoff(tasks=[init_task])
        
        self.turn_count = 1
        
        return str(result)
    
    def process_choice(self, choice: str) -> str:
        """
        Process a player choice using memory-enabled crew
        """
        self.turn_count += 1
        
        # Check if story should end
        if self.turn_count > self.max_turns:
            return self._generate_story_ending()
        
        print(f"\n⚙️ Processing choice: {choice}")
        print(f"🧠 Turn {self.turn_count}/{self.max_turns} - Memory system maintaining consistency...\n")
        
        from crewai import Task
        
        # Create memory-aware task
        choice_task = Task(
            description=f"""
            Continue the {self.current_theme} interactive fiction story based on player choice.
            
            PLAYER CHOICE: {choice}
            TURN: {self.turn_count} of {self.max_turns}
            
            CRITICAL - USE CREW MEMORY:
            The crew memory system has stored all previous story elements.
            - Character names, personalities, and relationships
            - Setting details and locations
            - Plot threads and conflicts
            - Story atmosphere and established facts
            
            MAINTAIN PERFECT CONSISTENCY with previous scenes using crew memory.
            
            COORDINATE ALL AGENTS:
            1. World Agent: Describe environment response to player choice
               - Use established settings from memory
               - Show consequences in the world
            
            2. Character Agent: Show character reactions to choice  
               - Use established character personalities from memory
               - Maintain relationship continuity
            
            3. Story Agent: Advance plot based on choice
               - Continue established plot threads from memory
               - Create meaningful consequences
               - Build toward resolution (turn {self.turn_count} of {self.max_turns})
            
            SYNTHESIZE into coherent scene that:
            - Directly responds to: {choice}
            - Maintains story consistency via crew memory
            - Advances toward natural conclusion
            - Ends with 2-3 clear numbered choices
            
            Remember: Crew memory ensures consistency automatically!
            """,
            agent=self.coordinator_agent.agent,
            expected_output="Consistent story continuation with new choices"
        )
        
        # Execute with memory
        result = self.crew.kickoff(tasks=[choice_task])
        
        # Generate image
        if self.image_agent:
            self._generate_scene_image(str(result))
        
        return str(result)
    
    def _generate_story_ending(self) -> str:
        """Generate story conclusion"""
        print("🎭 Creating story conclusion...")
        
        from crewai import Task
        
        ending_task = Task(
            description=f"""
            Create a satisfying conclusion for this {self.current_theme} story.
            
            FINAL TURN: {self.turn_count} of {self.max_turns}
            
            USE CREW MEMORY to create ending that:
            - Resolves main plot threads from memory
            - Provides character arc conclusions
            - References key player choices and consequences
            - Matches the established tone and genre
            
            Create: Satisfying, conclusive, and meaningful ending.
            """,
            agent=self.coordinator_agent.agent,
            expected_output="Complete story conclusion"
        )
        
        result = self.crew.kickoff(tasks=[ending_task])
        
        return f"🎭 STORY COMPLETE 🎭\n\n{str(result)}"
    
    def _generate_scene_image(self, scene_content: str):
        """Generate image for current scene"""
        try:
            print("🎨 Generating scene image...")
            image_info = self.image_agent.create_scene_image(
                story_content=scene_content,
                turn_number=self.turn_count,
                location="story_location",
                characters_present=[],
                mood="atmospheric"
            )
            
            if image_info.get("success"):
                print(f"✅ Image created: {image_info.get('filename', 'unknown')}")
                
        except Exception as e:
            print(f"⚠️ Image generation error: {e}")
    
    # Keep other methods from original crew...
    def _select_theme(self) -> str:
        """Interactive theme selection"""
        themes = {
            "1": "fantasy_adventure",
            "2": "sci_fi_exploration", 
            "3": "mystery_detective",
            "4": "horror_survival",
            "5": "modern_thriller",
            "6": "steampunk_adventure"
        }
        
        print("\n🎨 Choose your story theme:")
        for key, theme in themes.items():
            print(f"  {key}. {theme.replace('_', ' ').title()}")
        
        while True:
            choice = input("\nEnter your choice (1-6): ").strip()
            if choice in themes:
                return themes[choice]
            print("❌ Invalid choice. Please enter a number 1-6.")