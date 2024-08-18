import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QListWidget, QVBoxLayout, QWidget,
    QLabel, QListWidgetItem, QSplitter, QPushButton, QToolBar, QAction,
    QStackedWidget, QHBoxLayout, QFormLayout, QLineEdit, QTextEdit, QCheckBox, QComboBox, QSpacerItem, QSizePolicy, QStackedLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

class ClipApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Clip Viewer")
        self.setGeometry(100, 100, 800, 600)

        # Create a stacked widget to manage different pages
        self.stacked_widget = QStackedWidget()
        
        # Create the main page
        self.main_page = QWidget()
        self.main_layout = QHBoxLayout(self.main_page)

        # Add toolbar for user profile button
        self.toolbar = QToolBar("User Profile Toolbar")
        self.toolbar.setMovable(False)  # Optional: make toolbar unmovable
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)

        # Create a user profile button in the toolbar
        user_profile_action = QAction(QIcon(), "Profile", self)
        user_profile_action.triggered.connect(self.show_user_profile)
        self.toolbar.addAction(user_profile_action)

        # Make the toolbar align to the right
        spacer = QWidget()
        # spacer.setSizePolicy(QSpacerItem.Expanding, QSpacerItem.Fixed)
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
        splitter.setStretchFactor(1, 1)  # Make the main area stretchable

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
        self.name_edit.setText("John Doe")  # Pre-fill with example data
        form_layout.addRow("Name:", self.name_edit)

        self.email_edit = QLineEdit(self)
        self.email_edit.setText("john.doe@example.com")  # Pre-fill with example data
        form_layout.addRow("Email:", self.email_edit)

        self.bio_edit = QTextEdit(self)
        self.bio_edit.setText("This is a short bio about John Doe.")  # Pre-fill with example data
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


    

    