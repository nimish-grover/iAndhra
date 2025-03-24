import datetime
from zoneinfo import ZoneInfo
from app.db import db

class Ticket(db.Model):
    __tablename__ = 'tickets'
    def get_current_time():
        return datetime.now(ZoneInfo('Asia/Kolkata'))
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    username = db.Column(db.String(255),nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum('Open', 'In Progress', 'Resolved', 'Closed', name="ticket_status"), default='Open')
    priority = db.Column(db.Enum('Low', 'Medium', 'High', 'Critical', name="ticket_priority"), default='Medium')
    created_at = db.Column(db.DateTime, default=get_current_time)
    updated_at = db.Column(db.DateTime, default=get_current_time,onupdate=get_current_time)

    user = db.relationship('User', backref=db.backref('tickets', lazy=True))

    def __repr__(self):
        return f"<Ticket {self.id} - {self.status}>"

    def __init__(self, user_id,username,title,description,status,priority):
        self.user_id = user_id
        self.username = username
        self.title = title
        self.description = description
        self.status = status
        self.priority = priority

    def json(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.username,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority
        }
        
    @classmethod
    def get_all(cls):
        query=cls.query.order_by(cls.id.desc())
        return query
    
    @classmethod
    def check_duplicate(cls, lulc_id, bt_id):
        return cls.query.filter(cls.lulc_id==lulc_id, cls.bt_id==bt_id).first()

    def save_to_db(self):
        duplicate_item = self.check_duplicate(self.lulc_id, self.bt_id)
        if duplicate_item:
            duplicate_item.area = self.area
            duplicate_item.created_by = self.created_by
            duplicate_item.is_approved = self.is_approved
            duplicate_item.created_on = self.get_current_time()
        else:
            db.session.add(self)
        db.session.commit()

    def update_db(self):
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()