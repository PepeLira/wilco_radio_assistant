import sys
import time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QListWidget, QVBoxLayout, QWidget,
    QLabel, QListWidgetItem, QSplitter, QPushButton, QToolBar, QAction,
    QStackedWidget, QHBoxLayout, QFormLayout, QLineEdit, QTextEdit, QCheckBox, QSpacerItem, QSizePolicy, QStatusBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon
from audio_processor import AudioProcessor
from audio_input import AudioInput
from clip_divider import ClipDivider



class RecordingThread(QThread):
    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal()
    # Initialize the audio input and clip divider classes
    audio_input = AudioInput(blocksize=1024)
    clip_divider = ClipDivider(threshold=0.005, samplerate=44100)
    
    # Create the main audio processor
    audio_processor = AudioProcessor(audio_input, clip_divider)
    
    def __init__(self):
        super().__init__()
        self._is_running = False

    def run(self):
        self._is_running = True
        self.recording_started.emit()
        print("Recording started...")
        self.audio_processor.start()
        # Simulate recording process
        while self._is_running:
            time.sleep(1)

        print("Recording stopped...")
        self.audio_processor.stop()
        self.recording_stopped.emit()

    def stop(self):
        self._is_running = False

class ClipApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Clip Recorder")
        self.setGeometry(100, 100, 800, 600)

        # Initialize recording thread
        self.recording_thread = RecordingThread()

        # Connect signals for recording start/stop
        self.recording_thread.recording_started.connect(self.on_recording_started)
        self.recording_thread.recording_stopped.connect(self.on_recording_stopped)

        # Create a stacked widget to manage different pages
        self.stacked_widget = QStackedWidget()
        
        # Create the main page
        self.main_page = QWidget()
        self.main_layout = QHBoxLayout(self.main_page)

        # Add toolbar for user profile button
        self.toolbar = QToolBar("User Profile Toolbar")
        self.toolbar.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Add a label to the status bar
        self.status_label = QLabel("  Ready")
        self.status_bar.addWidget(self.status_label)

        # Add a button to the status bar
        self.status_button = QPushButton("R", self)
        self.status_button.setStyleSheet("""
            QPushButton {
                background-color: red;
                border-radius: 20px;
                width: 40px;
                height: 40px;
            }
            QPushButton:pressed {
                background-color: green;
            }
        """)
        self.status_button.setGeometry(750, 550, 40, 40)  # Adjust size and position
        self.status_button.clicked.connect(self.toggle_recording)
        self.status_bar.addPermanentWidget(self.status_button)












        # Create a user profile button in the toolbar
        user_profile_action = QAction(QIcon(), "Profile", self)
        user_profile_action.triggered.connect(self.show_user_profile)
        self.toolbar.addAction(user_profile_action)

        # Make the toolbar align to the right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.toolbar.addWidget(spacer)
        self.toolbar.addAction(user_profile_action)

        # Main splitter
        splitter = QSplitter(Qt.Horizontal)

        # Sidebar - List of dates
        self.date_list = QListWidget()
        self.date_list.setFixedWidth(200)
        self.date_list.itemClicked.connect(self.load_clips)

        # Add some dummy dates for testing
        dates = ["2024-08-15", "2024-08-14", "2024-08-13"]
        for date in dates:
            QListWidgetItem(date, self.date_list)

        # Main area - List of clips
        self.clip_display = QWidget()
        self.clip_layout = QVBoxLayout(self.clip_display)

        # Placeholder label to show selected clips
        self.clip_label = QLabel("Select a date to view clips", self)
        self.clip_label.setAlignment(Qt.AlignCenter)
        self.clip_layout.addWidget(self.clip_label)

        # Add sidebar and main area to the splitter
        splitter.addWidget(self.date_list)
        splitter.addWidget(self.clip_display)
        splitter.setStretchFactor(1, 1)

        # Add the splitter to the main layout
        self.main_layout.addWidget(splitter)

        # Add the main page to the stacked widget
        self.stacked_widget.addWidget(self.main_page)

        # Create the profile page
        self.profile_page = QWidget()
        self.profile_layout = QVBoxLayout(self.profile_page)

        # Add a form layout to display user information
        form_layout = QFormLayout()

        # Add user information fields
        self.name_edit = QLineEdit(self)
        self.name_edit.setText("John Doe")
        form_layout.addRow("Name:", self.name_edit)

        self.email_edit = QLineEdit(self)
        self.email_edit.setText("john.doe@example.com")
        form_layout.addRow("Email:", self.email_edit)

        self.bio_edit = QTextEdit(self)
        self.bio_edit.setText("This is a short bio about John Doe.")
        form_layout.addRow("Bio:", self.bio_edit)

        # Add the form layout to the profile page
        self.profile_layout.addLayout(form_layout)

        # Add a button to go back to the main page
        back_button = QPushButton("Back to Main", self)
        back_button.clicked.connect(self.show_main_page)
        self.profile_layout.addWidget(back_button)

        # Add the profile page to the stacked widget
        self.stacked_widget.addWidget(self.profile_page)

        # Set the stacked widget as the central widget
        self.setCentralWidget(self.stacked_widget)

        # Dummy clip data
        self.clip_data = {
            "2024-08-15": ["Clip 1", "Clip 2", "Clip 3"],
            "2024-08-14": ["Clip A", "Clip B"],
            "2024-08-13": ["Clip X", "Clip Y", "Clip Z"],
        }

        # Add a recording button on the bottom right
        # self.record_button = QPushButton(self)
        # self.record_button.setStyleSheet("""
        #     QPushButton {
        #         background-color: red;
        #         border-radius: 40px;
        #         width: 40px;
        #         height: 40px;
        #     }
        #     QPushButton:pressed {
        #         background-color: green;
        #     }
        # """)
        # self.record_button.setGeometry(750, 550, 40, 40)  # Adjust size and position
        # self.record_button.clicked.connect(self.toggle_recording)

        # State to track if recording is active
        self.is_recording = False

    def load_clips(self, item):
        selected_date = item.text()
        clips = self.clip_data.get(selected_date, [])

        # Clear previous clips from layout
        for i in reversed(range(self.clip_layout.count())): 
            widget_to_remove = self.clip_layout.itemAt(i).widget()
            if widget_to_remove:
                widget_to_remove.deleteLater()

        # Show clips of selected date with checkboxes
        if clips:
            for clip in clips:
                clip_checkbox = QCheckBox(clip, self)
                self.clip_layout.addWidget(clip_checkbox)
        else:
            no_clips_label = QLabel("No clips available for this date", self)
            no_clips_label.setAlignment(Qt.AlignCenter)
            self.clip_layout.addWidget(no_clips_label)

    def show_user_profile(self):
        # Switch to the profile page
        self.stacked_widget.setCurrentWidget(self.profile_page)

    def show_main_page(self):
        # Switch back to the main page
        self.stacked_widget.setCurrentWidget(self.main_page)

    def toggle_recording(self):
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        # Start recording in a new thread
        self.recording_thread.start()
        self.is_recording = True
        self.status_label.setText("  Recording...")
        self.status_button.setStyleSheet("""
            QPushButton {
                background-color: green;
                border-radius: 20px;
                width: 40px;
                height: 40px;
            }
        """)

    def stop_recording(self):
        # Stop the recording thread
        self.recording_thread.stop()
        self.recording_thread.wait()  # Ensure the thread is fully stopped
        self.is_recording = False
        self.status_label.setText("  Ready")
        self.status_button.setStyleSheet("""
            QPushButton {
                background-color: red;
                border-radius: 20px;
                width: 40px;
                height: 40px;
            }
        """)

    def on_recording_started(self):
        print("Recording started... (GUI update can be done here)")

    def on_recording_stopped(self):
        print("Recording stopped... (GUI update can be done here)")

def main():
    app = QApplication(sys.argv)
    window = ClipApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()


# class Clip:
#     client = OpenAI()

#     def __init__(self, clip_id, audio, time_start, time_end):
#         self.clip_id = clip_id
#         self.audio = audio
#         self.time_start = time_start
#         self.time_end = time_end
#         self.duration = time_end - time_start
#         self.date = time_start.date()
#         self.transcript = ''
#         self.entities = []
#         self.keywords = []
#         self.summary = ''

#     def transcribe_audio(self):
#         audio_file = open(self.audio, "rb")
#         transcription = client.audio.transcriptions.create(
#             model='whisper-1',
#             file=audio_file,
#             prompt="Transcribe the following audio clip, where the clip is always in chilean spanish",
#         )

#         return transcription.text

#     def extract_entities(self):
#         pass

#     def extract_keywords(self):
#         pass

#     def summarize(self):
#         pass

#     def __str__(self):
#         return f'Clip {self.clip_id }: {self.time_start}-{self.time_end}'

#     def __repr__(self):
#         return f'Clip {self.clip_id }: {self.time_start}-{self.time_end}'

    



# Side bar with days
# Main window with clips
# Clip details window
# Clip edit window
# Clip create window
# Clip delete window
# User settings window
# User login window
# User register window
# User forgot password window
# User change password window
# User change email window
# User change username window
# User delete account window
# User logout window
# User profile window


    

    