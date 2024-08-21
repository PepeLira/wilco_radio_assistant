from app.models.audio_clip import AudioClip
from peewee import DoesNotExist

class AudioClipController:

    @staticmethod
    def add_audio_clip(data):
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

    @staticmethod
    def get_audio_clip(clip_id):
        """Retrieve an AudioClip by ID."""
        try:
            return AudioClip.get(AudioClip.id == clip_id)
        except DoesNotExist:
            print("AudioClip not found.")
            return None

    @staticmethod
    def remove_audio_clip(clip_id):
        """Remove an AudioClip from the database by ID."""
        try:
            clip = AudioClip.get(AudioClip.id == clip_id)
            clip.delete_instance()
            return True
        except DoesNotExist:
            print("AudioClip not found.")
            return False
