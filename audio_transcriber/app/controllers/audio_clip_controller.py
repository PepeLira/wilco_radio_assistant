from app.models.audio_clip import AudioClip
from peewee import DoesNotExist

class AudioClipController:
    def __init__(self, current_user, view):
        self.current_user = current_user
        self.view = view

    def add_audio_clip(self, data):
        """Add a new AudioClip to the database."""
        try:
            clip = AudioClip.create(
                transcription=data["transcription"],
                summary=data["summary"],
                date=data["date"],
                time_start=data["time_start"],
                time_end=data["time_end"],
                duration=data["duration"],
                description=data["description"],
                score=data["score"],
                admin_user=data["admin_user"],
                file_path=data["file_path"]
            )
            return clip
        except Exception as e:
            print(f"Error adding audio clip: {e}")
            return None
    
    def get_audio_clip(self, clip_id):
        """Retrieve an AudioClip by ID."""
        try:
            return AudioClip.get(AudioClip.id == clip_id)
        except DoesNotExist:
            print("AudioClip not found.")
            return None
    
    def get_clips_by_date(self, date):
        """Retrieve all audio clips for a given date, ordered by start_time"""
        try:
            return list(AudioClip.select().where(AudioClip.admin_user == self.current_user, AudioClip.date == date).order_by(AudioClip.time_start))
        except DoesNotExist:
            print("AudioClip not found.")

    def remove_audio_clip(self, clip_id):
        """Remove an AudioClip from the database by ID"""
        try:
            clip = AudioClip.get(AudioClip.id == clip_id)
            clip.delete_instance()
            return True
        except DoesNotExist:
            print("AudioClip not found.")
            return False
        
    def get_clips_dates(self):
        """Retrieve all dates of audio clips of the current user order by date."""
        try:
            return list(set([clip.date for clip in AudioClip.select().where(AudioClip.admin_user == self.current_user)]))
        except DoesNotExist:
            print("AudioClip not found.")
            return None
        
    ## Update View methods
    
    def show_start_data(self):
        self.show_clip_dates()
        self.show_date_transcriptions()
        self.view.set_date_transcriptions_callback(self.show_date_transcriptions)

    def show_clip_dates(self):
        """Add a list of dates to the view."""
        dates = self.get_clips_dates()
        for date in dates:
            self.view.add_date(date)

    def show_date_transcriptions(self, date=None):
        self.view.clear_transcription_table()
        """Add a list of transcriptions for a given date to the view."""
        if date is None:
            date = self.get_clips_dates()[0]
            self.view.update_header_label(date)
        clips = self.get_clips_by_date(date)
        for clip in clips:
            time = f"{clip.time_start.strftime("%H:%M:%S")} - {clip.time_end.strftime("%H:%M:%S")}"
            self.view.add_transcription(clip.transcription, time)

