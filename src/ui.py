import http.server
import socketserver
import json
import webbrowser
import os
import sys
from urllib.parse import parse_qs

# Setup paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import game modules
try:
    from crew import fiction_crew
    from game_state import game_state
    GAME_READY = True
    print("Game loaded successfully")
except Exception as e:
    print(f"Failed to load game: {e}")
    GAME_READY = False
    sys.exit(1)

# Simple HTML interface
HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <title>Interactive Fiction</title>
    <style>
        body {
            font-family: monospace;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 20px;
            border: 1px solid #ccc;
        }
        .game-output {
            background: #000;
            color: #00ff00;
            padding: 15px;
            height: 400px;
            overflow-y: scroll;
            font-family: monospace;
            margin: 10px 0;
            border: 1px solid #333;
        }
        .input-area {
            display: flex;
            gap: 10px;
            margin: 10px 0;
        }
        input[type="text"] {
            flex: 1;
            padding: 8px;
            font-family: monospace;
            border: 1px solid #ccc;
        }
        button {
            padding: 8px 15px;
            background: #007cba;
            color: white;
            border: none;
            cursor: pointer;
        }
        button:hover {
            background: #005a87;
        }
        .status {
            background: #eee;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ccc;
        }
        .start-screen {
            text-align: center;
            padding: 40px;
        }
        .game-screen {
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <div id="start-screen" class="start-screen">
            <h1>Interactive Fiction Engine</h1>
            <p>Enter your name to begin:</p>
            <input type="text" id="player-name" placeholder="Your name">
            <br><br>
            <button onclick="startGame()">Start Game</button>
        </div>
        
        <div id="game-screen" class="game-screen">
            <div class="status">
                Player: <span id="status-name"></span> | 
                Turn: <span id="status-turn">0</span>/5 | 
                Location: <span id="status-location"></span>
            </div>
            
            <div class="game-output" id="output"></div>
            
            <div class="input-area">
                <input type="text" id="command-input" placeholder="Enter command" onkeypress="handleKeyPress(event)">
                <button onclick="sendCommand()">Send</button>
            </div>
            
            <div>
                <button onclick="quickCommand('look around')">Look</button>
                <button onclick="quickCommand('status')">Status</button>
                <button onclick="quickCommand('help')">Help</button>
                <button onclick="quickCommand('quit')">Quit</button>
            </div>
        </div>
    </div>

    <script>
        function startGame() {
            const name = document.getElementById('player-name').value.trim();
            if (!name) {
                alert('Please enter your name');
                return;
            }
            
            fetch('/start', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({name: name})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('start-screen').style.display = 'none';
                    document.getElementById('game-screen').style.display = 'block';
                    document.getElementById('status-name').textContent = name;
                    updateStatus(data.status);
                    addOutput('GAME', data.initial_scene);
                } else {
                    alert('Failed to start game: ' + data.error);
                }
            })
            .catch(error => {
                alert('Error: ' + error);
            });
        }
        
        function sendCommand() {
            const input = document.getElementById('command-input');
            const command = input.value.trim();
            if (!command) return;
            
            addOutput('YOU', command);
            input.value = '';
            
            fetch('/command', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({command: command})
            })
            .then(response => response.json())
            .then(data => {
                addOutput('GAME', data.response);
                updateStatus(data.status);
                
                if (data.game_ended) {
                    addOutput('SYSTEM', 'Game Over. Refresh page to play again.');
                    document.getElementById('command-input').disabled = true;
                }
            })
            .catch(error => {
                addOutput('ERROR', 'Failed to process command: ' + error);
            });
        }
        
        function quickCommand(cmd) {
            document.getElementById('command-input').value = cmd;
            sendCommand();
        }
        
        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendCommand();
            }
        }
        
        function addOutput(sender, text) {
            const output = document.getElementById('output');
            
            // Add spacing before each message for readability
            const spacer = document.createElement('div');
            spacer.innerHTML = '&nbsp;';
            output.appendChild(spacer);
            
            const line = document.createElement('div');
            line.textContent = sender + ': ' + text;
            output.appendChild(line);
            
            // Add extra spacing after GAME messages
            if (sender === 'GAME') {
                const extraSpacer = document.createElement('div');
                extraSpacer.innerHTML = '&nbsp;';
                output.appendChild(extraSpacer);
            }
            
            output.scrollTop = output.scrollHeight;
        }
        
        function updateStatus(status) {
            if (status) {
                if (status.turn) {
                    document.getElementById('status-turn').textContent = status.turn;
                }
                if (status.location) {
                    document.getElementById('status-location').textContent = status.location;
                }
            }
        }
    </script>
</body>
</html>"""

class GameHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            if self.path == '/start':
                response = self.handle_start(data)
            elif self.path == '/command':
                response = self.handle_command(data)
            else:
                response = {'success': False, 'error': 'Unknown endpoint'}
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            error_response = {'success': False, 'error': str(e)}
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode())
    
    def handle_start(self, data):
        try:
            player_name = data.get('name', 'Player')
            
            # Initialize player in game state
            game_state.update_player({"name": player_name})
            
            # Get initial scene
            initial_scene = fiction_crew.get_current_scene_description()
            
            # Get current status
            state = game_state.get_state()
            turn_info = game_state.get_turn_info()
            
            status = {
                'turn': f"{turn_info['current_turn']}/{turn_info['max_turns']}",
                'location': state['player']['location']
            }
            
            return {
                'success': True,
                'initial_scene': initial_scene,
                'status': status
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def handle_command(self, data):
        try:
            command = data.get('command', '').strip()
            
            if not command:
                return {'response': 'Please enter a command', 'status': self.get_status()}
            
            # Handle quit command
            if command.lower() in ['quit', 'exit']:
                return {
                    'response': 'Thanks for playing!',
                    'status': self.get_status(),
                    'game_ended': True
                }
            
            # Handle status command
            if command.lower() == 'status':
                state = game_state.get_state()
                player = state['player']
                turn_info = game_state.get_turn_info()
                
                status_text = f"Name: {player['name']}\n"
                status_text += f"Location: {player['location']}\n"
                status_text += f"Health: {player['health']}\n"
                status_text += f"Turn: {turn_info['current_turn']}/{turn_info['max_turns']}\n"
                status_text += f"Phase: {turn_info['phase']}"
                
                return {
                    'response': status_text,
                    'status': self.get_status(),
                    'game_ended': game_state.is_game_ended()
                }
            
            # Process command through game system (it handles turn incrementing)
            response = fiction_crew.process_user_input(command)
            
            return {
                'response': response,
                'status': self.get_status(),
                'game_ended': game_state.is_game_ended()
            }
            
        except Exception as e:
            return {
                'response': f"Error processing command: {str(e)}",
                'status': self.get_status(),
                'game_ended': False
            }
    
    def get_status(self):
        try:
            state = game_state.get_state()
            turn_info = game_state.get_turn_info()
            
            # Format location name nicely
            location = state['player']['location'] or 'Unknown'
            if location != 'Unknown':
                location = location.replace('_', ' ').title()
            
            return {
                'turn': f"{turn_info['current_turn']}/{turn_info['max_turns']}",
                'location': location
            }
        except Exception as e:
            print(f"Error getting status: {e}")
            return {'turn': '0/5', 'location': 'Unknown'}

def main():
    if not GAME_READY:
        print("Game not ready. Exiting.")
        return
    
    PORT = 8080
    
    print(f"Starting Interactive Fiction UI on port {PORT}")
    print(f"Open http://localhost:{PORT} in your browser")
    
    # Open browser automatically
    webbrowser.open(f'http://localhost:{PORT}')
    
    # Start server
    with socketserver.TCPServer(("", PORT), GameHandler) as httpd:
        try:
            print("Server running. Press Ctrl+C to stop.")
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

if __name__ == "__main__":
    main()