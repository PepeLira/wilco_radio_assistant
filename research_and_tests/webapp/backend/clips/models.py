from django.db import models
from accounts.models import Author


class Clip(models.Model):
    clip_id = models.CharField(max_length=255, primary_key=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    audio = models.FileField()
    time_start = models.DateTimeField()
    date = models.DateField()
    transcript = models.TextField()
    entities = models.TextField()
    keywords = models.TextField()
    summary = models.TextField()

    def __init__(self, clip_id, author, audio, time_start):
        self.clip_id = clip_id
        self.author = author
        self.audio = audio
        self.time_start = time_start
        self.date = clip_id.split('_')[1]
        self.transcript = ''
        self.entities = []
        self.keywords = []
        self.summary = ''

    def transcribe_audio(self):
        pass

    def extract_entities(self):
        pass

    def extract_keywords(self):
        pass

    def summarize(self):
        pass

    def __str__(self):
        return f'Clip {self.clip_id} by {self.author}'

    def __repr__(self):
        return f'Clip {self.clip_id} by {self.author}'