# minimal_ui.py - Ultra-simple UI without emojis

import http.server
import socketserver
import json
import webbrowser
import os
import sys
from urllib.parse import parse_qs

# Setup
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Try to import game - if it fails, use dummy mode
try:
    from crew import fiction_crew
    from game_state import game_state
    GAME_WORKING = True
    print("Game modules loaded!")
except Exception as e:
    print(f"Game modules failed, using demo mode: {e}")
    GAME_WORKING = False

# Simple game state for demo mode
demo_state = {
    'started': False,
    'player_name': '',
    'messages': [],
    'turn': 0
}

# Simple HTML interface
HTML = """<!DOCTYPE html>
<html><head>
<title>Narrative AI</title>
<style>
body { font-family: Arial; background: linear-gradient(45deg, #667eea, #764ba2); color: white; margin: 0; padding: 20px; }
.container { max-width: 800px; margin: 0 auto; }
.panel { background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; margin: 10px 0; }
.chat { height: 300px; overflow-y: scroll; background: rgba(0,0,0,0.2); padding: 15px; border-radius: 5px; margin: 10px 0; }
.message { margin: 10px 0; padding: 10px; border-radius: 5px; }
.user { background: rgba(100,149,237,0.3); text-align: right; }
.ai { background: rgba(152,251,152,0.3); }
input[type=text] { width: 70%; padding: 10px; border: none; border-radius: 5px; }
button { padding: 10px 15px; border: none; border-radius: 5px; background: #4CAF50; color: white; cursor: pointer; margin: 5px; }
button:hover { background: #45a049; }
.status { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 14px; }
</style>
</head><body>
<div class="container">
  <div class="panel" style="text-align: center;">
    <h1>Narrative AI</h1>
    <p>Multi-Agent Storytelling Experience</p>
  </div>
  
  <div id="start-screen" class="panel">
    <h2>Begin Your Adventure</h2>
    <input type="text" id="name" placeholder="Enter your name..." />
    <button onclick="startGame()">Start</button>
  </div>
  
  <div id="game-screen" class="panel" style="display:none;">
    <div class="chat" id="chat"></div>
    <input type="text" id="command" placeholder="What do you want to do?" onkeypress="if(event.key=='Enter')sendCommand()" />
    <button onclick="sendCommand()">Send</button>
    <br>
    <button onclick="quickCmd('look around')">Look Around</button>
    <button onclick="quickCmd('go north')">Go North</button>
    <button onclick="quickCmd('status')">Status</button>
    <button onclick="quickCmd('help')">Help</button>
    
    <div class="status" id="status">
      <div>Player: <span id="player-name">-</span></div>
      <div>Turn: <span id="turn">0</span>/5</div>
    </div>
  </div>
</div>

<script>
function startGame() {
  const name = document.getElementById('name').value;
  if (!name) { alert('Enter your name!'); return; }
  
  fetch('/start', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({name: name})
  }).then(r => r.json()).then(data => {
    if (data.success) {
      document.getElementById('start-screen').style.display = 'none';
      document.getElementById('game-screen').style.display = 'block';
      document.getElementById('player-name').textContent = name;
      addMessage('Game Master', data.message);
    }
  });
}

function sendCommand() {
  const cmd = document.getElementById('command').value;
  if (!cmd) return;
  
  addMessage('You', cmd);
  document.getElementById('command').value = '';
  
  fetch('/command', {
    method: 'POST', 
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({command: cmd})
  }).then(r => r.json()).then(data => {
    addMessage('AI Narrator', data.response);
    document.getElementById('turn').textContent = data.turn;
  });
}

function quickCmd(cmd) {
  document.getElementById('command').value = cmd;
  sendCommand();
}

function addMessage(sender, text) {
  const chat = document.getElementById('chat');
  const msg = document.createElement('div');
  msg.className = 'message ' + (sender.includes('You') ? 'user' : 'ai');
  msg.innerHTML = '<strong>' + sender + ':</strong><br>' + text;
  chat.appendChild(msg);
  chat.scrollTop = chat.scrollHeight;
}
</script>
</body></html>"""

class SimpleHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML.encode())
        else:
            super().do_GET()
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        response = {}
        
        if self.path == '/start':
            name = data.get('name', 'Hero')
            
            if GAME_WORKING:
                try:
                    game_state.update_player({"name": name})
                    scene = fiction_crew.get_current_scene_description()
                    response = {
                        'success': True, 
                        'message': f'Welcome {name}! Your adventure begins...\n\n{scene}'
                    }
                except Exception as e:
                    response = {'success': True, 'message': f'Welcome {name}! (Demo mode: {e})'}
            else:
                demo_state['started'] = True
                demo_state['player_name'] = name
                response = {
                    'success': True,
                    'message': f'Welcome {name}! You are in a mystical forest. (Demo Mode - Game modules not loaded)'
                }
        
        elif self.path == '/command':
            command = data.get('command', '')
            
            if GAME_WORKING:
                try:
                    demo_state['turn'] += 1
                    if command.lower() not in ['look', 'status', 'help']:
                        game_state.increment_turn()
                    
                    ai_response = fiction_crew.process_user_input(command)
                    turn_info = game_state.get_turn_info()
                    
                    response = {
                        'response': ai_response,
                        'turn': turn_info['current_turn']
                    }
                except Exception as e:
                    response = {
                        'response': f'Error: {e}',
                        'turn': demo_state['turn']
                    }
            else:
                # Demo responses
                demo_state['turn'] += 1
                demo_responses = {
                    'look': 'You see a beautiful forest with tall trees and mysterious shadows.',
                    'go north': 'You walk north through the forest.',
                    'status': f"You are {demo_state['player_name']}, healthy and ready for adventure!",
                    'help': 'Try: look, go north, status, or describe what you want to do.'
                }
                
                demo_response = demo_responses.get(command.lower(), f'You {command}. The forest responds with mysterious energy.')
                response = {
                    'response': demo_response + ' (Demo Mode)',
                    'turn': demo_state['turn']
                }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

def main():
    PORT = 8081
    
    print("Starting Narrative AI...")
    print(f"Open http://localhost:{PORT} in your browser")
    
    if GAME_WORKING:
        print("Full game mode enabled!")
    else:
        print("Demo mode - game modules not loaded")
    
    # Open browser
    webbrowser.open(f'http://localhost:{PORT}')
    
    # Start server
    with socketserver.TCPServer(("", PORT), SimpleHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nGoodbye!")

if __name__ == "__main__":
    main()