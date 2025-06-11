# Interactive Fiction Engine

A multi-agent interactive fiction system powered by CrewAI and OpenAI, designed for the Intelligent Agents course assignment 2025.

## Overview

This project implements a sophisticated multi-agent system that creates dynamic, choice-driven interactive fiction experiences. Four specialized AI agents collaborate through intelligent delegation to generate immersive 5-turn storytelling adventures:

- **Game Coordinator** - Intelligently analyzes user input and delegates to appropriate agents
- **World Builder** - Creates detailed locations, environments, and manages the game world
- **Character Manager** - Handles NPCs, dialogue, and character interactions with continuity
- **Story Director** - Manages plot progression, meaningful choices, and narrative flow

## Assignment Requirements Met

✅ **Multi-agent collaboration** - 4 agents working together through structured workflow  
✅ **LLM-based system** - Uses OpenAI GPT-4 models through CrewAI framework  
✅ **Effective agent communication** - Single Source of Truth GameState architecture  
✅ **User interaction** - Simple web interface for player input/output  
✅ **Complex problem solving** - Dynamic storytelling with intelligent agent selection  
✅ **Working memory/state** - Persistent game state managed across all agents  
✅ **Custom tools** - Specialized tools for each agent to modify shared state

## Key Features

- **Intelligent Agent Selection** - Coordinator analyzes intent and selects appropriate agents
- **Single Source of Truth** - All agents read/write to shared GameState for consistency
- **Dynamic World Generation** - World Builder creates unique locations based on player choices
- **Character Continuity** - Character Manager maintains NPC presence and dialogue consistency
- **5-Turn Adventure Structure** - Story progression through beginning → middle → late → climax phases
- **Simple Web Interface** - Clean, terminal-style UI for easy interaction

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Run the System

For simple web interface:
```bash
python simple_ui.py
```

For command-line interface:
```bash
python main.py
```

## Project Structure

```
src/
├── requirements.txt          # Python dependencies
├── .env                     # API keys (create this)
├── main.py                  # Command-line game loop
├── simple_ui.py            # Web interface
├── crew.py                  # Multi-agent crew orchestration
├── game_state.py           # Single Source of Truth state management
└── agents/
    ├── __init__.py         # Agent exports
    ├── coordinator_agent.py # Intelligent coordination and delegation
    ├── world_agent.py      # Dynamic world creation
    ├── character_agent.py  # NPC management and dialogue
    └── story_agent.py      # Plot progression and choices
```

## How to Play

The game starts with a dynamically generated world. Each playthrough creates a unique 5-turn adventure:

### Available Commands
- **Movement**: `go north`, `travel east`, `enter cave`
- **Exploration**: `look around`, `examine room`, `inspect item`
- **Interaction**: `talk to wizard`, `speak with character`, `ask about quest`
- **System**: `status`, `help`, `quit`

### Game Flow
1. **Turn 0**: Dynamic world generation and initial scene
2. **Turns 1-5**: Player choices shape the unique narrative
3. **End**: Comprehensive story summary and epilogue generation

## Technical Architecture

### Multi-Agent Coordination
- **Intelligent Delegation** - Coordinator uses intent analysis to select agents
- **Sequential Processing** - Agents work in coordinated sequence through CrewAI
- **GameState Integration** - All agents use tools to modify shared state
- **Character Continuity** - System tracks NPC presence and prevents disappearance

### Single Source of Truth
```
Agent Tools → GameState (Shared State) ← All Agents Read From
```

- **Locations**: World data stored centrally
- **Characters**: NPC data with location tracking  
- **Story Events**: Narrative progression logged
- **Player State**: Location, inventory, choices tracked

### Agent Specialization

**Game Coordinator**
- Intent analysis and agent selection
- Simple request handling
- GameState status reporting

**World Builder**  
- `create_starting_world` - Generates unique themed worlds
- `create_location` - Adds new areas dynamically
- `move_player` - Updates player location

**Character Manager**
- `create_character` - Adds NPCs to scenes
- `handle_character_dialogue` - Processes conversations
- `get_character_context` - Maintains continuity

**Story Director**
- `create_story_choices` - Generates meaningful options
- `advance_story` - Progresses narrative
- `create_story_narrative` - Generates summaries and conclusions

## Problems Solved

### 1. Agent Confabulation
**Problem**: Agents generated descriptions inconsistent with actual GameState  
**Solution**: Single Source of Truth architecture - all descriptions read from GameState

### 2. Character Continuity  
**Problem**: NPCs disappeared between turns without explanation  
**Solution**: Intelligent agent selection automatically includes Character Manager when NPCs present

### 3. Turn Counting Issues
**Problem**: UI and game system both incremented turns causing confusion  
**Solution**: Centralized turn management in main game system only

### 4. UI Readability
**Problem**: Poor message separation in terminal output  
**Solution**: Automatic spacing between USER and GAME messages

## Key Achievements

- **Seamless Agent Collaboration** - 4 agents working through intelligent delegation
- **Consistent World State** - Single Source of Truth prevents contradictions  
- **Dynamic Content Generation** - Unique worlds and stories each playthrough
- **Character Continuity** - NPCs maintain presence and personality
- **Simple Yet Functional UI** - Clean web interface with terminal aesthetics

## Future Enhancements

- **Extended Turn Limits** - Longer adventures with chapter progression
- **Save/Load System** - Persistent game sessions
- **Enhanced UI** - Improved styling and mobile support
- **Image Generation** - Visual representations of scenes
- **Multiplayer Support** - Shared world experiences

## Assignment Deliverables

1. **Source Code** - Complete implementation with all agents and tools
2. **Technical Report** - Architecture documentation with flow diagrams  
3. **Demo Video** - Working system demonstration with agent coordination

---

*Interactive Fiction Engine - Demonstrating intelligent multi-agent collaboration for dynamic storytelling through CrewAI framework.*