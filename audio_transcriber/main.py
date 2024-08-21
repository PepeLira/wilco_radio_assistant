from data.database import initialize_db, close_db
from app.controllers.admin_user_controller import AdminUserController
from app.controllers.audio_clip_controller import AudioClipController
from app.services.audio_input import AudioInput
from app.services.clip_divider import ClipDivider
from app.services.speech_2_text import Speech2Text
from app.services.audio_processor import AudioProcessor
from datetime import datetime

def main():
    # Initialize the database
    initialize_db()

    # Initialize the audio input and clip divider classes
    print("Initializing models...")
    audio_input = AudioInput()
    clip_divider = ClipDivider()
    speech2text = Speech2Text()

    # Initialize the controllers
    user_controller = AdminUserController()
    clip_controller = AudioClipController()

    # generate a new default user
    user_controller.add_admin_user("admin", "admin", "admin")

    # Create the main audio processor
    audio_processor = AudioProcessor(audio_input, clip_divider, speech2text, 
                                    user_controller, clip_controller)
    clip_divider.add_observer(audio_processor)

    # Start processing
    audio_processor.start()

    # if key pressed, stop the audio_processor
    print("Press any key to stop...")
    input()
    audio_processor.stop()

    # Close the database connection
    close_db()

if __name__ == '__main__':
    main()