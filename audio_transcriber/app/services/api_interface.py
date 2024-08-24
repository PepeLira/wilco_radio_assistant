import requests
import json
from data.database import db, initialize_db, close_db
from app.models.audio_clip import AudioClip
from peewee import DoesNotExist
import pdb

class ApiInterface:
    def __init__(self):
        self.url = "https://wilco-backend-production.up.railway.app/"
        self.post_clips_endpoint = "api/clips/"

    def parse_clip(self, clip):
        date = clip.date.replace("/", "-")
        time_start = clip.time_start.__str__()
        time_end = clip.time_end.__str__()
        clip_dict = {
            "user_id": 1,
            "transcription": clip.transcription,
            "date": date,
            "time_start": f"{date}T{time_start}Z",
            "time_end": f"{date}T{time_end}Z",
            "duration": int(clip.duration),
            "score": clip.score
        }
        return clip_dict

    def post_clip(self, clip):
        route = self.url + self.post_clips_endpoint
        clip_data = self.parse_clip(clip)
        response = requests.post(route, json=clip_data)
        print("Response", response.status_code, response.text)
        return response
    
    def start_database(self):
        initialize_db()

    def close_database(self):
        close_db()

    def get_clips_by_date(self, date):
        try:
            return [clip
                for clip in AudioClip.select()
                .where(
                    AudioClip.admin_user == 1, 
                    AudioClip.date == date
                )
                .order_by(AudioClip.time_start)
            ]
        except DoesNotExist:
            print("AudioClip not found.")

    def post_clips_by_date(self, date):
        clips = self.get_clips_by_date(date)
        for clip in clips:
            self.post_clip(clip)


if __name__ == '__main__':
    api = ApiInterface()
    api.start_database()
    date = "2024/08/22"
    post_clips_by_date = api.post_clips_by_date(date)
    api.close_database()
