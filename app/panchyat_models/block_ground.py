from datetime import datetime
from zoneinfo import ZoneInfo
from app.db import db


class BlockGround(db.Model):
    def get_current_time():
        return datetime.now(ZoneInfo('Asia/Kolkata'))
    
    __tablename__ = 'block_groundwater'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    extraction = db.Column(db.Float, nullable=False)
    bt_id = db.Column(db.ForeignKey('block_territory.id'), nullable=False)
    is_approved = db.Column(db.Boolean, nullable=False, default=False)
    created_on = db.Column(db.DateTime, default=get_current_time)
    created_by = db.Column(db.ForeignKey('users.id'), nullable=False)
    
    users = db.relationship('User', backref=db.backref('block_groundwater', lazy='dynamic'))
    block_territory = db.relationship('BlockTerritory', backref=db.backref('block_groundwater', lazy='dynamic'))
    
    def __init__(self,extraction, bt_id, is_approved, created_by):
        self.extraction = extraction
        self.bt_id = bt_id
        self.is_approved = is_approved
        self.created_by = created_by
        
    def json(self):
        return {
            "id":self.id,
            "extraction":self.extraction,
            "bt_id":self.bt_id,
            "is_approved":self.is_approved,
            "created_by":self.created_by,
            "creatd_on":self.created_on
        }
    @classmethod
    def get_block_groundwater_data(cls, bt_id):
        query = db.session.query(
            cls.extraction,
            cls.is_approved
        ).filter(cls.bt_id == bt_id)

        results = query.first()

        if results:
            json_data = {'extraction': results[0],'is_approved':results[1]} 
            return json_data
        else:
            return None

    @classmethod
    def get_by_bt_id(cls, bt_id):
        query =  cls.query.filter(cls.bt_id==bt_id)
        results = query.all()

        if results:
            json_data = [item.json() for item in results]
            return json_data
        else:
            return None
        
    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter(cls.id==id).first()
    
    @classmethod
    def check_duplicate(cls, bt_id):
        return cls.query.filter( cls.bt_id==bt_id).first()
    
    def update_db(self):
        db.session.commit()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()