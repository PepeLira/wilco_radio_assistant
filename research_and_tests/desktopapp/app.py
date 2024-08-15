import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Create a vertical layout
        vbox = QVBoxLayout()

        # Create a label and a button
        self.label = QLabel('Hello, PyQt!', self)
        button = QPushButton('Click Me', self)

        button.clicked.connect(self.on_click)

        # Add widgets to the layout
        vbox.addWidget(self.label)
        vbox.addWidget(button)

        # Set the layout for the main window
        self.setLayout(vbox)

        self.setWindowTitle('My First PyQt App')
        self.setGeometry(100, 100, 600, 400)
        self.show()

    def on_click(self):
        self.label.setText('Button Clicked!')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())






class Clip:
    client = OpenAI()

    def __init__(self, clip_id, audio, time_start, time_end):
        self.clip_id = clip_id
        self.audio = audio
        self.time_start = time_start
        self.time_end = time_end
        self.duration = time_end - time_start
        self.date = time_start.date()
        self.transcript = ''
        self.entities = []
        self.keywords = []
        self.summary = ''

    def transcribe_audio(self):
        audio_file = open(self.audio, "rb")
        transcription = client.audio.transcriptions.create(
            model='whisper-1',
            file=audio_file,
            prompt="Transcribe the following audio clip, where the clip is always in chilean spanish",
        )

        return transcription.text

    def extract_entities(self):
        pass

    def extract_keywords(self):
        pass

    def summarize(self):
        pass

    def __str__(self):
        return f'Clip {self.clip_id }: {self.time_start}-{self.time_end}'

    def __repr__(self):
        return f'Clip {self.clip_id }: {self.time_start}-{self.time_end}'

    



    

    