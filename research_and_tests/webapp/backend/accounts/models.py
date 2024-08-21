from django.db import models

# Create your models here.
class Author(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    bio = models.TextField()

    def __init__(self, name, email, bio):
        self.name = name
        self.email = email
        self.bio = bio

    def __str__(self):
        return f'Author {self.name}'

    def __repr__(self):
        return f'Author {self.name}'