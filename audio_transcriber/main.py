from data.database import initialize_db, close_db
from app.controllers.admin_user_controller import AdminUserController
from app.controllers.audio_clip_controller import AudioClipController
from app.services.audio_input import AudioInput
from app.services.clip_divider import ClipDivider
from app.services.speech_2_text import Speech2Text
from app.services.audio_processor import AudioProcessor
from PyQt5.QtWidgets import QApplication
from app.views.main_ui import MainUI
import sys

def main():
    # Initialize the database
    initialize_db()

    # Initialize the audio input and clip divider classes
    print("Initializing models...")
    audio_input = AudioInput()
    clip_divider = ClipDivider()
    speech2text = Speech2Text()

    # Start the UI
    app = QApplication(sys.argv)
    ui = MainUI()

    # Initialize the controllers
    user_controller = AdminUserController()
    # if no user generate a new default user
    if user_controller.get_admin_user(user_id=1) is None:
        user_controller.add_admin_user(name="admin", email="admin", company="admin")

    clip_controller = AudioClipController(user_controller.get_admin_user(user_id=1), ui)

    # Create the main audio processor
    audio_processor = AudioProcessor(audio_input, clip_divider, speech2text, 
                                    user_controller, clip_controller)
    clip_divider.add_observer(audio_processor)

    # Set the callbacks
    ui.set_record_button_callback(audio_processor.start)
    ui.set_stop_button_callback(audio_processor.stop)
    
    ui.show()

    clip_controller.show_start_data()
    if sys.flags.interactive != 1:
        close_db()
        sys.exit(app.exec_())

if __name__ == '__main__':
    main()