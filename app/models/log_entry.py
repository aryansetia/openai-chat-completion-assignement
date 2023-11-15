from datetime import datetime
import pytz
from app import db

class LogEntry(db.Model):
    __tablename__ = 'log_entry'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)  
    prompt = db.Column(db.String(255), nullable=False)
    response = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.DateTime(timezone=True), default=datetime.now(pytz.timezone('Asia/Kolkata')))

    # constructor method to initialize the class
    def __init__(self, user_id, prompt, response=None):
        self.user_id = user_id
        self.prompt = prompt
        self.response = response

    # save method to save data to db
    def save(self):
        db.session.add(self)
        db.session.commit()

    # method to get all entries
    @classmethod
    def get_all_entries(cls): 
        return cls.query.all()
