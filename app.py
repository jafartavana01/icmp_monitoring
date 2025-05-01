from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
from ping3 import ping
import threading
import time
import json

app = Flask(__name__)
socketio = SocketIO(app)

# Store monitored hosts
monitored_hosts = {}

def ping_host(host):
    while host in monitored_hosts:
        try:
            response_time = ping(host, timeout=1)
            if response_time is None or response_time is False:
                status = {'host': host, 'time': time.time(), 'response': None, 'status': 'timeout'}
            else:
                status = {'host': host, 'time': time.time(), 'response': round(response_time * 1000, 2), 'status': 'success'}
            socketio.emit('ping_update', status)
        except Exception as e:
            status = {'host': host, 'time': time.time(), 'response': None, 'status': 'error', 'error': str(e)}
            socketio.emit('ping_update', status)
        time.sleep(1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_host', methods=['POST'])
def add_host():
    host = request.json.get('host')
    if host and host not in monitored_hosts:
        monitored_hosts[host] = threading.Thread(target=ping_host, args=(host,))
        monitored_hosts[host].daemon = True
        monitored_hosts[host].start()
        return jsonify({'status': 'success', 'message': f'Now monitoring {host}'})
    return jsonify({'status': 'error', 'message': 'Invalid host or already monitoring'})

@app.route('/remove_host', methods=['POST'])
def remove_host():
    host = request.json.get('host')
    if host in monitored_hosts:
        del monitored_hosts[host]
        return jsonify({'status': 'success', 'message': f'Stopped monitoring {host}'})
    return jsonify({'status': 'error', 'message': 'Host not found'})

if __name__ == '__main__':
    socketio.run(app, debug=True)