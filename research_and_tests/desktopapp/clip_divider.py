import numpy as np
import wave
import time
import os

class ClipDivider:
    def __init__(self, threshold, samplerate, channels=1, next_clip_margin=0.5, min_clip=1):
        self.threshold = threshold
        self.samplerate = samplerate
        self.channels = channels
        self.next_clip_margin = next_clip_margin  # Time to wait before closing the clip
        self.min_clip = min_clip  # Minimum clip length in seconds
        self.buffer = []
        self.clip_start_time = None
        self.last_below_threshold_time = None
        self.in_clip = False

        # Ensure the clips/ directory exists
        self.clip_dir = 'clips'
        if not os.path.exists(self.clip_dir):
            os.makedirs(self.clip_dir)

    def calculate_rms(self, block):
        """Calculate the RMS of an audio block."""
        return np.sqrt(np.mean(np.square(block)))

    def add_block(self, block):
        """Add an audio block and process it to detect clips."""
        rms = self.calculate_rms(block)
        current_time = time.time()

        if rms > self.threshold:
            if not self.in_clip:
                self.in_clip = True
                self.clip_start_time = current_time
                self.buffer = []

            self.buffer.append(block)
            self.last_below_threshold_time = None  # Reset this since we are above the threshold

        elif self.in_clip:
            if self.last_below_threshold_time is None:
                self.last_below_threshold_time = current_time
                self.buffer.append(block)  # Continue adding blocks while waiting for next_clip_margin to pass

            elif current_time - self.last_below_threshold_time <= self.next_clip_margin:
                self.buffer.append(block)  # Add the block within the margin time

            else:
                self.close_clip()
                self.in_clip = False

    def close_clip(self):
        """Close and save the clip if it meets the minimum length requirement."""
        clip_length_in_seconds = len(self.buffer) * len(self.buffer[0]) / self.samplerate
        if clip_length_in_seconds >= self.min_clip:
            print(f"Audio clip length: {clip_length_in_seconds:.2f} seconds")
            # Here you'd save the clip to a WAV file instead of just printing
            self.save_clip_to_wav()
        else:
            print("Clip discarded because it was too short.")
        self.buffer = []  # Clear the buffer after saving or discarding the clip

    def save_clip_to_wav(self):
        """Save the audio clip buffer to a WAV file."""
        # Generate a filename based on the current date and time
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        clip_time_seconds = int(time.time())
        filename = os.path.join(self.clip_dir, f"clip_{timestamp}_{clip_time_seconds}.wav")

        audio_data = np.concatenate(self.buffer)
        audio_data_int = np.int16(audio_data * 32767)

        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)  # Assuming 16-bit audio
            wf.setframerate(self.samplerate)
            wf.writeframes(audio_data_int.tobytes())
        
        print(f"Clip saved as {filename}")

