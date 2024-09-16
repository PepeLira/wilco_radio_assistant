import ffmpeg
import numpy as np
import matplotlib.pyplot as plt
from collections import deque
from threading import Thread, Event
import pyaudio
import wave
import os
import time
import logging

logging.basicConfig(
    level=logging.INFO,  # Set log level to INFO or DEBUG for more detailed logs
    format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s',
    handlers=[
        # logging.FileHandler("audio_log.log"),  # Logs to a file
        logging.StreamHandler()                # Also logs to the console
    ]
)

# Audio settings
STREAM_URL = "https://s1-bos.liveatc.net/scel?nocache=2024090522535685913"
BUFFER_SIZE = 44100 # 1 second buffer for 44.1kHz audio (adjust buffer size for smoothness)
SAMPLE_RATE = 44100  # assuming stream is 44.1kHz
CHUNK_SIZE = 4096  # Audio chunk size for playback and plotting


class AudioStreamPlotter:
    def __init__(self, stream_url, buffer_size=44100, sample_rate=44100, chunk_size=4096, clip_folder="audio_clips"):
        self.stream_url = stream_url
        self.buffer_size = buffer_size
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        
        # Control variables for audio and graphing
        self.enable_audio = False
        self.enable_plot = False
        self.enable_recording = False

        # Threshold settings for recording
        self.threshold = 50
        self.recording_delta_time = 4  # Time in seconds
        self.chunk_duration = chunk_size / sample_rate
        self.recording_folder = clip_folder
        self.min_clip_duration = 2  # Minimum clip duration in seconds

        # Queue to hold audio data
        self.audio_queue = deque(maxlen=self.buffer_size)
        self.record_queue = deque(maxlen=self.buffer_size*20)
        
        # PyAudio settings
        self.p = pyaudio.PyAudio()
        self.stream = None

        # Plot settings
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [])
        self.ax.set_title("Smoothed Audio Signal")
        self.ax.set_xlabel("Time (seconds)")
        self.ax.set_ylabel("Amplitude")

        # Thread and event management
        self.streaming_thread = None
        self.recording_thread = None
        self.stop_event = Event()

        # Create the folder for saving audio clips if it doesn't exist
        os.makedirs(self.recording_folder, exist_ok=True)

    def stream_audio(self):
        process = (
            ffmpeg
            .input(self.stream_url)
            .output('pipe:', format='wav', acodec='pcm_s16le', ac=1, ar=self.sample_rate)
            .run_async(pipe_stdout=True)
        )

        while self.enable_audio and not self.stop_event.is_set():
            in_bytes = process.stdout.read(self.chunk_size)
            if not in_bytes:
                break
            
            # Play the audio in real-time
            if self.stream and self.enable_audio:
                self.stream.write(in_bytes)
            
            # Convert audio bytes to samples for plotting
            samples = np.frombuffer(in_bytes, dtype=np.int16)
            self.audio_queue.extend(samples)
            self.record_queue.append(samples)

    def smooth_signal(self, signal, window_size=50):
        return np.convolve(signal, np.ones(window_size) / window_size, mode='valid')

    def update_plot(self):
        time_axis = np.linspace(0, self.buffer_size / self.sample_rate, num=self.buffer_size)
        while self.enable_plot and not self.stop_event.is_set():
            if len(self.audio_queue) >= self.buffer_size:
                # Get the latest samples from the queue
                current_audio = np.array(list(self.audio_queue))
                
                # Smooth the signal if desired (optional)
                smoothed_audio = self.smooth_signal(current_audio)
                
                # Update the plot with the smoothed signal
                self.line.set_data(time_axis[:len(smoothed_audio)], smoothed_audio)
                
                # Adjust the x and y limits dynamically
                self.ax.set_xlim(0, self.buffer_size / self.sample_rate)
                self.ax.set_ylim(np.min(smoothed_audio), np.max(smoothed_audio))
                
                plt.pause(0.01)  # Pause to allow for smooth plotting

    def start_audio_stream(self):
        if self.enable_audio:
            self.stream = self.p.open(format=pyaudio.paInt16,
                                      channels=1,
                                      rate=self.sample_rate,
                                      output=True)
            self.streaming_thread = Thread(target=self.stream_audio)
            self.streaming_thread.daemon = True
            self.streaming_thread.start()

    def start_plot(self):
        if self.enable_plot:
            self.update_plot()

    def start_recording_thread(self):
        if self.enable_recording:
            self.recording_thread = Thread(target=self.record_audio_clips)
            self.recording_thread.daemon = True
            self.recording_thread.start()

    def record_audio_clips(self):
        recording = False
        clip_data = []
        silence_time = 0

        while self.enable_recording and not self.stop_event.is_set():
            if len(self.record_queue) > 0:
                current_audio = self.record_queue.popleft()
                mean_value = np.mean(np.abs(current_audio))
                if mean_value > self.threshold:
                    if not recording:
                        print("Start recording")
                    recording = True
                    silence_time = 0
                    clip_data.extend(current_audio)
                elif recording:
                    silence_time += self.chunk_duration
                    clip_data.extend(current_audio)
                    if silence_time >= self.recording_delta_time:
                        print("Stop recording")
                        if len(clip_data)/self.sample_rate > self.min_clip_duration:
                            self.save_clip(clip_data)
                        else:
                            print("Clip too short, not saving")
                        recording = False
                        clip_data = []

            time.sleep(0.1)  # Add a small delay to reduce CPU usage

    def save_clip(self, clip_data):
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = os.path.join(self.recording_folder, f"clip_{timestamp}.wav")

        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(self.sample_rate)
            wf.writeframes(np.array(clip_data, dtype=np.int16).tobytes())

        print(f"Saved clip: {filename}")

    def stop_audio_stream(self):
        self.stop_event.set()

        if self.streaming_thread and self.streaming_thread.is_alive():
            self.streaming_thread.join()

        if self.recording_thread and self.recording_thread.is_alive():
            self.recording_thread.join()

        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()

    def run(self):
        # Start the audio stream, plotting, and recording as needed
        if self.enable_audio:
            self.start_audio_stream()
        
        if self.enable_recording:
            self.start_recording_thread()
        
        if self.enable_plot:
            self.start_plot()
        

# Example usage
audio_plotter = AudioStreamPlotter(STREAM_URL)

# Enable PyAudio stream, graphing, and recording
audio_plotter.enable_audio = True  # Set to True to enable audio stream
audio_plotter.enable_plot = True   # Set to True to enable real-time graph
audio_plotter.enable_recording = True  # Set to True to enable audio recording

audio_plotter.run()

# Stop the audio stream and threads after usage
audio_plotter.stop_audio_stream()
