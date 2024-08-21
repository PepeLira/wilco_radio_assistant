from peewee import CharField, Model
from data.database import db

class AdminUser(Model):
    name = CharField()
    email = CharField(unique=True)
    company = CharField()

    class Meta:
        database = db