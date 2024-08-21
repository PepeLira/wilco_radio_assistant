from peewee import SqliteDatabase

# Initialize the database connection
db = SqliteDatabase('radio_transcriber.db')

def initialize_db():
    # Import models here to avoid circular imports
    from app.models.admin_user import AdminUser
    from app.models.audio_clip import AudioClip

    # Connect to the database
    db.connect()
    
    # Create tables
    db.create_tables([AdminUser, AudioClip], safe=True)

def close_db():
    if not db.is_closed():
        db.close()

