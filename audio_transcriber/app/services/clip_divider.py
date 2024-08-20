import numpy as np
import wave
import scipy.signal as signal
import time
import os
from clip_notifier import ClipNotifier

class ClipDivider(ClipNotifier):
    def __init__(self, threshold, samplerate, block_size, channels=1, next_clip_margin=0.5, min_clip=1):
        super().__init__()
        self.threshold = threshold
        self.samplerate = samplerate
        self.block_size = block_size
        self.channels = channels
        self.next_clip_margin = next_clip_margin  # Time to wait before closing the clip
        self.min_clip = min_clip  # Minimum clip length in seconds
        self.buffer = []
        self.clip_start_time = None
        self.last_below_threshold_time = None
        self.in_clip = False
        self.margin_cicles_count = 0 # To know how many blocks to remove

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
        block_duration = len(block) / self.samplerate # in seconds

        if rms > self.threshold:
            # print("RMS:", rms)

            if not self.in_clip:
                self.in_clip = True
                self.buffer = []
            
            self.margin_cicles_count = 0
            self.buffer.append(block)
            self.last_below_threshold_time = None  # Reset this since we are above the threshold
        
        elif self.in_clip:
            if self.last_below_threshold_time is None:
                self.last_below_threshold_time = block_duration
                self.buffer.append(block)  # Continue adding blocks while waiting for next_clip_margin to pass
                self.margin_cicles_count += 1

            elif (self.last_below_threshold_time + block_duration) <= self.next_clip_margin:
                self.buffer.append(block)  # Add the block within the margin time
                self.last_below_threshold_time += block_duration
                self.margin_cicles_count += 1

            else:
                self.remove_margin_blocks()
                self.close_clip()
                self.in_clip = False

    def remove_margin_blocks(self):
        """Remove the margin blocks from the buffer."""
        if self.margin_cicles_count > 0:
            self.buffer = self.buffer[:-self.margin_cicles_count]

    def close_clip(self):
        """Close and save the clip if it meets the minimum length requirement."""
        self.clip_length_in_seconds = len(self.buffer) * self.block_size / self.samplerate
        if self.clip_length_in_seconds >= self.min_clip:
            print(f"Audio clip length: {self.clip_length_in_seconds:.2f} seconds")
            self.save_clip_to_wav()
        else:
            print("Clip discarded because it was too short.")
        self.buffer = []  # Clear the buffer after saving or discarding the clip

    def bandpass_filter(self, audio_data):
        # Update the sampling frequency to match the audio file's sample rate
        nyquist = 0.5 * self.samplerate
        low_cutoff = 80  # Low cutoff frequency in Hz
        high_cutoff = 2000  # High cutoff frequency in Hz
        low = low_cutoff / nyquist
        high = high_cutoff / nyquist

        # Design the bandpass filter with updated frequencies
        sos = signal.iirfilter(
            N=4,
            Wn=[low, high],
            btype='band',
            ftype='butter',
            output='sos'
        )

        # Apply the SOS filter to the audio signal
        filtered_audio_data = signal.sosfilt(sos, audio_data)
        return filtered_audio_data

    def save_clip_to_wav(self):
        """Save the audio clip buffer to a WAV file."""
        # Generate a file_path based on the current date and time
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        self.clip_length_in_seconds = int(self.clip_length_in_seconds)
        file_path = os.path.join(self.clip_dir, f"clip_{timestamp}_{self.clip_length_in_seconds}.wav")

        audio_data = np.concatenate(self.buffer)
        # audio_data = self.bandpass_filter(audio_data)
        audio_data_int = np.int16(audio_data * 32767)

        # Using a try-finally block to ensure the file is closed properly
        with wave.open(file_path, 'wb') as wf:
            try:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # Assuming 16-bit audio
                wf.setframerate(self.samplerate)
                wf.writeframes(audio_data_int.tobytes())
            finally:
                wf.close()  # Ensures the file is closed properly even if an error occurs
        # Logic to create a clip
        self.notify_observers(file_path)  # Notify observers about the new clip
        print(f"Clip saved as {file_path}")
