from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

class MCPServer:
    def __init__(self):
        self.app = app

    def run(self, host='0.0.0.0', port=5000):
        self.app.run(host=host, port=port)

    @app.route('/execute', methods=['POST'])
    def execute_command():
        data = request.json
        command = data.get('command')
        if not command:
            return jsonify({'error': 'No command provided'}), 400
        
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return jsonify({'stdout': result.stdout, 'stderr': result.stderr, 'returncode': result.returncode})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    server = MCPServer()
    server.run()