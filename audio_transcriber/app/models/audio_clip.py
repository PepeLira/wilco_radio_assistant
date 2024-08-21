from peewee import Model, TextField, DateTimeField, TimeField, FloatField, ForeignKeyField
from .admin_user import AdminUser
from data.database import db

class AudioClip(Model):
    transcription = TextField()
    summary = TextField(null=True)
    date = DateTimeField()
    time_start = TimeField()
    time_end = TimeField()
    duration = FloatField()
    description = TextField()
    score = FloatField()
    admin_user = ForeignKeyField(AdminUser, backref='audio_clips')
    file_path = TextField()

    class Meta:
        database = db