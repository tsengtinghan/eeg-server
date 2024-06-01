from flask import Flask
from flask_socketio import SocketIO, emit, send
import random
import time
import threading

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

def generate_eeg_data():
    while True:
        eeg_data = '1' if random.random() > 0.5 else '0'
        process_input(eeg_data)
        time.sleep(0.1)        

def process_input(value):
    if value == '1' or value == '0':
        socketio.emit('eegData', value)
        print('Sent EEG data: ' + value)


@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('my response', {'data': 'Connected'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('message')
def handle_message(msg):
    print('Received message: ' + msg)
    send('Message received: ' + msg)

if __name__ == '__main__':
    thread = threading.Thread(target=generate_eeg_data)
    thread.daemon = True  # Ensures thread exits when the main program exits
    thread.start()
    socketio.run(app, debug=True, port=5001)
