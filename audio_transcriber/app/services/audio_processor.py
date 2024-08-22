import threading
import queue
from .audio_input import AudioInput
from .clip_divider import ClipDivider
from .speech_2_text import Speech2Text

class AudioProcessor:
    def __init__(self, audio_input, clip_divider, speech_to_text, user_controller, \
                clip_controller):
        self.audio_input = audio_input
        self.clip_divider = clip_divider
        self.speech_to_text = speech_to_text
        self.running = False
        self.processed_files = set()
        self.new_clip_paths = queue.Queue()
        self.clip_controller = clip_controller
        self.user_controller = user_controller

    def update(self, clip_path):
        """Add the new clip to the queue of clips to transcribe."""
        self.new_clip_paths.put(clip_path)

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
            try:
                clip_path = self.new_clip_paths.get(timeout=1)  # Wait for a new clip path
                if clip_path and clip_path.endswith(".wav") and clip_path not in self.processed_files:
                    # Transcribe the new audio file
                    clip_data = self.speech_to_text.transcribe_clip(clip_path)
                    clip_data["admin_user"] = self.clip_controller.current_user
                    # Add the clip to the database
                    print(self.clip_controller.add_audio_clip(clip_data))
                    print("Transcription complete:", clip_data)

                    # Mark file as processed
                    self.processed_files.add(clip_path)
            except queue.Empty:
                continue  # No new clip paths available

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
    audio_input = AudioInput()
    clip_divider = ClipDivider()
    s2t = Speech2Text()
    
    # Create the main audio processor
    audio_processor = AudioProcessor(audio_input, clip_divider, s2t)
    
    clip_divider.add_observer(audio_processor)
    
    
    # Start processing
    audio_processor.start()

    # time.sleep(30)
    
    # Stop processing
    #audio_processor.stop()
