import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QListWidget
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QPushButton
from PyQt5.QtGui import QPixmap

class MainUI(QWidget):
    def __init__(self):
        super().__init__()

        # Styling parameters
        self.header_font_size = "18px"
        self.header_font_weight = "bold"
        self.icon_size = 32
        self.logo_font_size = "18px"
        self.logo_font_weight = "bold"
        self.init_ui()

    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout()

        # Initialize all UI components
        self.init_header(main_layout)
        self.init_content(main_layout)
        self.add_bottom_record_bar(main_layout)

        # Set main layout
        self.setLayout(main_layout)
        self.setWindowTitle('WilCo - Radio Transcription')
        self.setGeometry(100, 100, 800, 600)

    def init_header(self, layout):
        """Initialize the header layout with date, user icon, and logo."""
        header_layout = QHBoxLayout()

        # Header Label
        self.header_label = QLabel("Current Date: Transcriptions Date")
        self.header_label.setStyleSheet(f"font-size: {self.header_font_size}; font-weight: {self.header_font_weight};")
        header_layout.addWidget(self.header_label)

        # Right header layout (user icon and logo)
        right_header_layout = QHBoxLayout()
        self.user_icon = QLabel()
        user_pixmap = QPixmap('path_to_user_icon.png')  # Replace with the path to your user icon image
        self.user_icon.setPixmap(user_pixmap.scaled(self.icon_size, self.icon_size))
        right_header_layout.addWidget(self.user_icon)

        header_layout.addLayout(right_header_layout)
        header_layout.addStretch(1)

        layout.addLayout(header_layout)

    def init_content(self, layout):
        """Initialize the content layout with dates list and transcription table."""
        content_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()
        
        self.init_search_bar(left_layout)
        self.add_dates_list(left_layout)
        self.add_transcription_table(right_layout)

        content_layout.addLayout(left_layout)
        content_layout.addLayout(right_layout)

        content_layout.setStretch(0, 1)
        content_layout.setStretch(1, 5)

        layout.addLayout(content_layout)

    def init_search_bar(self, layout):
        """Initialize the search bar layout."""
        search_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search...")
        search_layout.addWidget(self.search_bar)

        layout.addLayout(search_layout)

    def add_dates_list(self, layout):
        self.dates_list = QListWidget()
        layout.addWidget(self.dates_list)
        self.dates_list.itemClicked.connect(self.on_date_selected)

    def add_transcription_table(self, layout):
        self.transcription_table = QTableWidget(0, 2)
        self.transcription_table.setHorizontalHeaderLabels(["Transcription", "Time"])
        self.transcription_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.transcription_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.transcription_table.setFrameStyle(QFrame.NoFrame)
        layout.addWidget(self.transcription_table)

    def clear_transcription_table(self):
        self.transcription_table.setRowCount(0)

    def clear_dates_list(self):
        self.dates_list.clear()

    def add_date(self, date_str):
        """Add a date to the dates list."""
        self.dates_list.addItem("📅 " + date_str)

    def add_transcription(self, transcription, time):
        """Add a transcription to the transcription table."""
        row_position = self.transcription_table.rowCount()
        self.transcription_table.insertRow(row_position)
        self.transcription_table.setItem(row_position, 0, QTableWidgetItem(transcription))
        self.transcription_table.setItem(row_position, 1, QTableWidgetItem(time))

    def add_bottom_record_bar(self, layout):
        """Add a bottom bar with buttons."""
        bottom_bar_layout = QHBoxLayout()

        # Log text
        self.log_text = QLabel("Log:")
        bottom_bar_layout.addWidget(self.log_text)

        # Record button
        self.record_button = QPushButton("Start Recording")
        bottom_bar_layout.addWidget(self.record_button)
        self.record_button.clicked.connect(self.record_button_clicked)

        # Stop button
        self.stop_button = QPushButton("Stop Recording")
        bottom_bar_layout.addWidget(self.stop_button)
        self.stop_button.clicked.connect(self.stop_button_clicked)

        bottom_bar_layout.setStretch(0, 8)
        bottom_bar_layout.setStretch(1, 2)
        bottom_bar_layout.setStretch(2, 2)

        layout.addLayout(bottom_bar_layout)

    def record_button_clicked(self):
        self.log_text.setText("Recording...")
        self.record_button.setEnabled(False)

    def update_header_label(self, date):
        """Update the header label with the current date."""
        self.header_label.setText(f"Current Date: {date}")

    def on_date_selected(self, item):
        """Slot method to handle date selection."""
        selected_date = item.text().replace("📅 ", "")  # Extract date from the item text
        self.update_header_label(selected_date)
        self.show_transcriptions_callback(selected_date)

    def set_date_transcriptions_callback(self, show_transcriptions_callback):
        """Set the callback to show transcriptions for a given date."""
        self.show_transcriptions_callback = show_transcriptions_callback

    def set_stop_button_callback(self, stop_button_clicked):
        """Set the callback for the stop button."""
        self.stop_button_clicked_call = stop_button_clicked

    def stop_button_clicked(self):
        self.log_text.setText("Recording stopped.")
        self.record_button.setEnabled(True)
        self.stop_button_clicked_call()
    
    def set_record_button_callback(self, record_button_clicked):
        """Set the callback for the record button."""
        self.record_button_clicked_call = record_button_clicked

    def record_button_clicked(self):
        self.log_text.setText("Recording...")
        self.record_button.setEnabled(False) 
        self.record_button_clicked_call()

def main():
    app = QApplication(sys.argv)
    ex = MainUI()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
