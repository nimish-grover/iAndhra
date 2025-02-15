from zoneinfo import ZoneInfo

from sqlalchemy import func
from app.db import db
from datetime import datetime

from app.models.waterbody import WaterbodyType

class BlockWaterbody(db.Model):
    def get_current_time():
        return datetime.now(ZoneInfo('Asia/Kolkata'))
    
    __tablename__ = 'block_waterbodies'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    count = db.Column(db.Integer, nullable=False)
    area = db.Column(db.Float, nullable=False)
    storage = db.Column(db.Float, nullable=False)
    is_approved = db.Column(db.Boolean, nullable=False, default=False)
    created_on = db.Column(db.DateTime, default=get_current_time)
    wb_type_id = db.Column(db.ForeignKey('waterbody_types.id'), nullable=False)
    bt_id = db.Column(db.ForeignKey('block_territory.id'), nullable=False)
    created_by = db.Column(db.ForeignKey('users.id'), nullable=False)
    
    users = db.relationship('User', backref=db.backref('block_waterbodies', lazy='dynamic'))
    waterbodies = db.relationship('WaterbodyType', backref=db.backref('block_waterbodies', lazy='dynamic'))
    block_territory = db.relationship('BlockTerritory', backref=db.backref('block_waterbodies', lazy='dynamic'))
    
    
    def __init__(self, wb_type_id, count, storage, bt_id, is_approved, created_by):
        self.wb_type_id = wb_type_id
        self.count = count
        self.area = 0
        self.storage = storage
        self.bt_id = bt_id
        self.is_approved = is_approved
        self.created_by = created_by
        
    def json(self):
        return {
            "id":self.id,
            "wb_type_id":self.wb_type_id,
            "area":self.area,
            "storage":self.storage,
            "count":self.count,
            "bt_id":self.bt_id,
            "is_approved":self.is_approved,
            "created_by":self.created_by,
            "creatd_on":self.created_on
        }
    
    @classmethod
    def get_by_bt_id(cls, bt_id):
        query = db.session.query(
            cls.id, 
            func.coalesce(cls.bt_id, bt_id).label('bt_id'),
            func.coalesce(cls.storage,0).label('storage'),
            func.coalesce(cls.count,0).label('count'),
            func.coalesce(cls.is_approved, None).label('is_approved'),
            WaterbodyType.id.label('wb_type_id'),
            WaterbodyType.waterbody_name
        ).outerjoin(
            cls,
            (WaterbodyType.id == cls.wb_type_id) &
            (cls.bt_id == bt_id)
        ).order_by(WaterbodyType.waterbody_name)
        
        results = query.all()

        if results:
            json_data = [{
                'id':index + 1,
                'table_id': item.id,
                'bt_id': item.bt_id, 
                'wb_type_id':item.wb_type_id,
                'storage':item.storage, 
                'count':item.count, 
                'is_approved':item.is_approved,
                'waterbody_name':item.waterbody_name} 
                for index,item in enumerate(results)]
            return json_data
        else:
            return None
    
    @classmethod
    def get_block_waterbody_data(cls, bt_id):
        query = db.session.query(
            WaterbodyType.id,
            WaterbodyType.waterbody_name,
            cls.storage,
            cls.count,
            cls.is_approved
        ).join(WaterbodyType, WaterbodyType.id == cls.wb_type_id
        ).filter(cls.bt_id == bt_id
        ).order_by(cls.storage)

        results = query.all()

        if results:
            json_data = [{
                'entity_id':item.id,
                'entity_name': item.waterbody_name,
                'entity_count': item.count,
                'entity_consumption': item.storage,
                'is_approved': item.is_approved
            } for item in results]
            return json_data
        else:
            return None

    @classmethod  
    def get_by_id(cls, id):
        return cls.query.filter(cls.id==id).first()
    
    @classmethod
    def check_duplicate(cls, wb_type_id, bt_id):
        return cls.query.filter(cls.wb_type_id==wb_type_id, cls.bt_id==bt_id).first()
    
    def update_db(self):
        db.session.commit()

    def save_to_db(self):
        duplicate_item = self.check_duplicate(self.wb_type_id, self.bt_id)
        if duplicate_item:
            duplicate_item.storage = self.storage
            duplicate_item.created_by = self.created_by
            duplicate_item.created_on = BlockWaterbody.get_current_time()
            duplicate_item.is_approved = self.is_approved
            duplicate_item.count = self.count
            # duplicate_item.update_db()
        else:
            db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()