from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
from flask_cors import CORS
from ping3 import ping
import threading
import time
from datetime import datetime

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

monitored_hosts = {}
host_history = {}
MAX_HISTORY = 100

def ping_host(host):
    while host in monitored_hosts:
        try:
            response_time = ping(host, timeout=1)
            timestamp = datetime.now().isoformat()
            
            if response_time is None or response_time is False:
                status = {
                    'host': host,
                    'timestamp': timestamp,
                    'response': None,
                    'status': 'DOWN',
                    'lastSeen': monitored_hosts[host].get('lastSeen')
                }
            else:
                response_ms = round(response_time * 1000, 2)
                status = {
                    'host': host,
                    'timestamp': timestamp,
                    'response': response_ms,
                    'status': 'UP',
                    'lastSeen': timestamp
                }
            
            # Update host status
            monitored_hosts[host].update(status)
            
            # Update history
            if host not in host_history:
                host_history[host] = []
            host_history[host].append(status)
            if len(host_history[host]) > MAX_HISTORY:
                host_history[host].pop(0)
            
            socketio.emit('ping_update', status)
            
        except Exception as e:
            status = {
                'host': host,
                'timestamp': datetime.now().isoformat(),
                'response': None,
                'status': 'ERROR',
                'error': str(e),
                'lastSeen': monitored_hosts[host].get('lastSeen')
            }
            socketio.emit('ping_update', status)
        
        time.sleep(1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/hosts', methods=['GET'])
def get_hosts():
    return jsonify({
        'hosts': list(monitored_hosts.values()),
        'total': len(monitored_hosts)
    })

@app.route('/api/hosts/<host>/history', methods=['GET'])
def get_host_history(host):
    if host in host_history:
        return jsonify({
            'history': host_history[host],
            'total': len(host_history[host])
        })
    return jsonify({'error': 'Host not found'}), 404

@app.route('/api/hosts', methods=['POST'])
def add_host():
    host = request.json.get('host')
    if host and host not in monitored_hosts:
        monitored_hosts[host] = {
            'host': host,
            'status': 'PENDING',
            'added': datetime.now().isoformat()
        }
        thread = threading.Thread(target=ping_host, args=(host,))
        thread.daemon = True
        thread.start()
        return jsonify({'status': 'success', 'message': f'Now monitoring {host}'})
    return jsonify({'status': 'error', 'message': 'Invalid host or already monitoring'}), 400

@app.route('/api/hosts/<host>', methods=['DELETE'])
def remove_host(host):
    if host in monitored_hosts:
        del monitored_hosts[host]
        if host in host_history:
            del host_history[host]
        return jsonify({'status': 'success', 'message': f'Stopped monitoring {host}'})
    return jsonify({'status': 'error', 'message': 'Host not found'}), 404

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)