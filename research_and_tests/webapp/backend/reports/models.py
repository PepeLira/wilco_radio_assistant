from django.db import models
from clips.models import Clip
from accounts.models import Author

# Create your models here.

class Report(models.Model):
    report_id = models.CharField(max_length=255, primary_key=True)
    audio_clips = models.ManyToManyField('clips.Clip')
    author = models.ForeignKey('accounts.Author', on_delete=models.CASCADE)
    summary = models.TextField()
    report_objective = models.ForeignKey('ReportObjective', on_delete=models.CASCADE)
    date = models.DateField()

    def __init__(self, report_id, author, report_objective):
        self.report_id = report_id
        self.audio_clips = []
        self.author = author
        self.summary = ''
        self.report_objective = report_objective
        self.date = report_id.split('_')[1]


class ReportObjective(models.Model):
    sentence = models.TextField()