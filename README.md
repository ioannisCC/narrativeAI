# Interactive Fiction Engine 🎮

A multi-agent interactive fiction system powered by CrewAI and OpenAI, designed for the Intelligent Agents course assignment 2025.

## 🌟 Overview

This project implements a sophisticated multi-agent system that creates dynamic interactive fiction experiences. Four specialized AI agents collaborate to generate immersive storytelling:

- **🏗️ World Builder Agent** - Creates locations, environments, and manages the game world
- **👥 Character Manager Agent** - Handles NPCs, dialogue, and character interactions  
- **📖 Story Director Agent** - Manages plot progression, choices, and narrative consistency
- **🎯 Game Coordinator Agent** - Orchestrates agent collaboration and user interaction

## 🎯 Assignment Requirements Met

✅ **Multi-agent collaboration** - 4 agents working together in structured workflow  
✅ **LLM-based system** - Uses OpenAI GPT models through CrewAI framework  
✅ **Agent communication** - Shared game state and inter-agent delegation  
✅ **User interaction** - Command-line interface for player input/output  
✅ **Complex problem solving** - Dynamic storytelling and world building  
✅ **Working memory/state** - Persistent game state across all agents  
✅ **Tool usage** - Custom tools + web search capabilities  

## 🚀 Features

- **Dynamic World Generation** - Agents create locations and environments on-demand
- **Interactive NPCs** - Character agents generate dialogue and personalities
- **Branching Narratives** - Story choices that affect game progression
- **Persistent Game State** - All agents share and update game world state
- **Web-Enhanced Content** - Agents can search web for inspiration
- **Real-time Collaboration** - Agents work together to respond to player actions

## 📋 Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL_NAME=gpt-3.5-turbo
```

### 3. Run the Game

```bash
python main.py
```

## 🏗️ Project Structure

```
fiction_engine/
├── requirements.txt          # Python dependencies
├── .env                     # API keys (create this)
├── main.py                  # Main game loop and UI
├── crew.py                  # Multi-agent crew orchestration
├── game_state.py           # Shared state management
├── agents/
│   ├── world_builder.py    # World/environment agent
│   ├── character_manager.py # NPC and dialogue agent
│   ├── story_director.py   # Plot and narrative agent
│   └── game_coordinator.py # Coordination agent
└── README.md               # This file
```

## 🎮 How to Play

The game starts in a forest clearing. You can interact using natural language commands:

### Movement Commands
- `go north` - Move to another location
- `travel east` - Travel in a direction
- `enter cave` - Enter specific locations

### Interaction Commands  
- `look around` - Examine surroundings
- `talk to wizard` - Speak with NPCs
- `take sword` - Pick up items
- `examine map` - Look at specific objects

### System Commands
- `status` - Check player status
- `help` - Show available commands
- `quit` - Exit the game

## 🤖 Agent Workflow

1. **User Input** → Game Coordinator analyzes the command
2. **Coordination** → Determines which agents are needed
3. **Parallel Processing** → Relevant agents work on their aspects
4. **Integration** → Coordinator combines all agent outputs
5. **Response** → Cohesive story response delivered to player

## 🛠️ Technical Implementation

### Multi-Agent Architecture
- **CrewAI Framework** - Manages agent collaboration
- **Sequential Processing** - Agents work in coordinated sequence
- **Shared State** - Global game state accessible to all agents
- **Tool Integration** - Custom tools + web search capabilities

### State Management
- **Persistent World** - Locations, items, and NPCs maintained
- **Player Progress** - Choices, inventory, and stats tracked
- **Story Events** - Narrative progression logged
- **Agent Memory** - Each agent has access to full context

### Agent Communication
- **Direct Tool Calls** - Agents use shared state tools
- **Delegation** - Coordinator can delegate to specialists
- **Context Sharing** - All agents see current game state
- **Event Logging** - Actions recorded for continuity

## 📊 Team Member Contributions

- **Member 1** - World Builder Agent & environment systems
- **Member 2** - Character Manager Agent & NPC interactions
- **Member 3** - Story Director Agent & narrative engine
- **Member 4** - Game Coordinator Agent & system integration

## 🔧 Dependencies

- `crewai` - Multi-agent framework
- `openai` - LLM integration
- `python-dotenv` - Environment configuration
- `langchain` - LLM tooling support
- `pydantic` - Data validation

## 🎯 Future Enhancements

- **GUI Interface** - Web-based or desktop interface
- **Save/Load System** - Persistent game sessions
- **Advanced NPCs** - More complex character behaviors
- **Multimedia Content** - Images and audio integration
- **Multiplayer Support** - Multiple players in same world

## 📝 Assignment Deliverables

1. **✅ Source Code** - Complete implementation in GitHub repo
2. **✅ Technical Report** - Architecture and implementation details  
3. **✅ Demo Video** - Working system demonstration

## 🏆 Key Achievements

- **Seamless Agent Collaboration** - 4 agents working in harmony
- **Dynamic Content Generation** - Story elements created on-demand
- **Persistent Game World** - Consistent state across all interactions
- **Natural Language Interface** - Intuitive player commands
- **Extensible Architecture** - Easy to add new agents/features

---

*Built with ❤️ for the Intelligent Agents course - demonstrating the power of multi-agent collaboration in interactive storytelling.*