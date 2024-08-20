import threading
import queue
from audio_input import AudioInput
from clip_divider import ClipDivider

class AudioProcessor:
    def __init__(self, audio_input, clip_divider):
        self.audio_input = audio_input
        self.clip_divider = clip_divider
        self.running = False

    def process_audio(self):
        """Continuously process audio blocks until stopped."""
        while self.running:
            try:
                block = self.audio_input.read_block()
                self.clip_divider.add_block(block)
            except queue.Empty:
                pass  # No block available, just continue

    def start(self):
        """Start the audio processing."""
        self.running = True
        self.audio_input.start_stream()

        # Run audio processing in a separate thread
        self.processing_thread = threading.Thread(target=self.process_audio)
        self.processing_thread.start()

    def stop(self):
        """Stop the audio processing."""
        self.running = False
        self.processing_thread.join()
        self.audio_input.stop_stream()

# Example usage:
if __name__ == '__main__':
    import time

    # Initialize the audio input and clip divider classes
    blocksize = 1024
    audio_input = AudioInput(blocksize=blocksize)
    clip_divider = ClipDivider(threshold=0.01, samplerate=44100, block_size=blocksize)
    
    # Create the main audio processor
    audio_processor = AudioProcessor(audio_input, clip_divider)
    
    # Start processing
    audio_processor.start()

    time.sleep(30)
    
    # Stop processing
    audio_processor.stop()
