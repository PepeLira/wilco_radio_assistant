import threading
import queue
from audio_input import AudioInput
from clip_divider import ClipDivider
from speech_2_text import Speech2Text
import time
import os

class AudioProcessor:
    def __init__(self, audio_input, clip_divider, speech_to_text):
        self.audio_input = audio_input
        self.clip_divider = clip_divider
        self.speech_to_text = speech_to_text
        self.running = False
        self.processed_files = set()

    def process_audio(self):
        """Continuously process audio blocks until stopped."""
        while self.running:
            try:
                block = self.audio_input.read_block()
                self.clip_divider.add_block(block)
            except queue.Empty:
                pass  # No block available, just continue

    def transcribe_new_clips(self):
        """Continuously check for new clips and transcribe them."""
        while self.running:
            for filename in os.listdir(self.speech_to_text.clips_path):
                file_path = os.path.join(self.speech_to_text.clips_path, filename)
                if filename.endswith(".wav") and file_path not in self.processed_files:
                    # Transcribe the new audio file
                    transcript, score = self.speech_to_text.transcribe_clip(file_path)
                    print(f"Transcribed: {transcript} with score: {score}")

                    # Mark file as processed
                    self.processed_files.add(file_path)
            time.sleep(1)  # Polling interval

    def start(self):
        """Start the audio processing and transcription."""
        self.running = True
        self.audio_input.start_stream()

        # Run audio processing in a separate thread
        self.processing_thread = threading.Thread(target=self.process_audio)
        self.processing_thread.start()

        # Run transcription in a separate thread
        self.transcription_thread = threading.Thread(target=self.transcribe_new_clips)
        self.transcription_thread.start()

    def stop(self):
        """Stop the audio processing and transcription."""
        self.running = False
        self.processing_thread.join()
        self.transcription_thread.join()
        self.audio_input.stop_stream()

# Example usage:
if __name__ == '__main__':
    import time

    # Initialize the audio input and clip divider classes
    blocksize = 1024
    audio_input = AudioInput(blocksize=blocksize)
    clip_divider = ClipDivider(threshold=0.01, samplerate=44100, block_size=blocksize)
    s2t = Speech2Text()
    
    # Create the main audio processor
    audio_processor = AudioProcessor(audio_input, clip_divider, s2t)
    
    # Start processing
    audio_processor.start()

    # time.sleep(30)
    
    # Stop processing
    audio_processor.stop()
