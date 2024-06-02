from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import serial
import time
import numpy as np

soundCard = "A1"
chunk_size = 512  # Number of samples per chunk
sampling_rate = 2000  # Sampling rate in Hz
beta_freq_range = (12, 30)  # Beta frequency range in Hz

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize serial communication
ser = serial.Serial('/dev/tty.usbmodem21301', 2000000)  # Change '/dev/cu.usbmodem1401' to the appropriate port on your system

def setup():
    print("Setup completed.")

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def test_connect():
    print('Client connected')

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

def loop():
    while True:
        print("Reading data...")
        # Read chunk of data from Arduino
        data_chunk = []
        for _ in range(chunk_size):
            ser.write(b"r" + soundCard.encode() + b"\n")
            alphaData = int(ser.readline().strip())
            data_chunk.append(alphaData)
        print("Data read.")

        # Perform FFT
        print("Performing FFT...")
        fft_result = np.fft.fft(data_chunk)
        fft_freqs = np.fft.fftfreq(chunk_size, 1/sampling_rate)
        print("FFT completed.")

        # Find indices corresponding to beta frequency range
        beta_indices = np.where((fft_freqs >= beta_freq_range[0]) & (fft_freqs <= beta_freq_range[1]))[0]

        # Print FFT result for beta range
        print("FFT result for beta range:")
        beta_amplitudes = []
        for i in beta_indices:
            beta_amplitudes.append(np.abs(fft_result[i]))
            print("Frequency:", fft_freqs[i], "Hz, Amplitude:", np.abs(fft_result[i]))

        # Calculate average amplitude for beta range
        avg_beta_amplitude = np.mean(beta_amplitudes)
        print("Average amplitude for beta range:", avg_beta_amplitude)

        socketio.emit('average_amplitude', avg_beta_amplitude)
        print("Sent average amplitude to client.")

        time.sleep(0.08)  # Wait for 80 milliseconds before the next read

@socketio.on('start_loop')
def start_loop():
    socketio.start_background_task(loop)

if __name__ == "__main__":
    setup()
    
    # Start the Flask server
    socketio.run(app, port=5001)
