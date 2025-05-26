from datetime import datetime
from zoneinfo import ZoneInfo
from app.db import db

class Feedback(db.Model):
    def get_current_time():
        return datetime.now(ZoneInfo('Asia/Kolkata'))
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=True)
    message = db.Column(db.Text, nullable=False)
    file_path = db.Column(db.String(255), nullable=True)
    submitted_at = db.Column(db.DateTime, default=get_current_time)
    
    def __init__(self, category, email, message, file_path):
        self.category = category
        self.email = email
        self.message = message
        self.file_path = file_path
        
    def json(self):
        return {
            'id': self.id,
            'category': self.category,
            'email': self.email,
            'message': self.message,
            'file_path': self.file_path,
            'submitted_at': self.submitted_at
        }
        
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
        
    def update_db(self):
        db.session.commit()
        
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
        
    @classmethod
    def get_feedback_by_id(cls, feedback_id):
        result = cls.query.filter_by(id=feedback_id).first()
        if result:
            return result.json()
        else:
            return None
        
    @classmethod
    def get_all_feedback(cls):
        results = cls.query.order_by(cls.submitted_at.desc()).all()
        if results:
            return [feedback.json() for feedback in results]
        else:
            return []
        
    @classmethod
    def get_feedback_by_category(cls, category):
        results = cls.query.filter_by(category=category).all()
        if results:
            return [feedback.json() for feedback in results]
        else:
            return []
        
    @classmethod
    def get_feedback_by_email(cls, email):
        results = cls.query.filter_by(email=email).all()
        if results:
            return [feedback.json() for feedback in results]
        else:
            return []