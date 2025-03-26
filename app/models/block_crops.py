from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import desc, func
from app.db import db
from app.models.crops import Crop

class BlockCrop(db.Model):
    def get_current_time():
        return datetime.now(ZoneInfo('Asia/Kolkata'))
    
    __tablename__ = 'block_crops'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    crop_id = db.Column(db.ForeignKey('crops.id'), nullable=False)
    area = db.Column(db.Float, nullable=False)
    bt_id = db.Column(db.ForeignKey('block_territory.id'), nullable=False)
    created_on = db.Column(db.DateTime, default=get_current_time)
    created_by = db.Column(db.ForeignKey('users.id'), nullable=False)
    is_approved = db.Column(db.Boolean, nullable=False, default=False)
    
    users = db.relationship('User', backref=db.backref('block_crops', lazy='dynamic'))
    block_territory = db.relationship('BlockTerritory', backref=db.backref('block_crops', lazy='dynamic'))
    crops = db.relationship('Crop', backref=db.backref('block_crops', lazy='dynamic'))
    
    def __init__(self,crop_id,area,bt_id,created_by,is_approved):
        self.crop_id = crop_id
        self.area = area
        self.bt_id = bt_id
        self.is_approved = is_approved
        self.created_by = created_by
        
    def json(self):
        return {
            "id":self.id,
            "crop_id":self.crop_id,
            "area":self.area,
            "bt_id":self.bt_id,
            "isAprroved":self.is_approved,
            "created_by":self.created_by,
            "creatd_on":self.created_on
        }
    
    @classmethod
    def get_by_bt_id(cls, bt_id):
        query = db.session.query(
            func.coalesce(cls.id, None).label('table_id'), 
            Crop.id.label('crop_id'), 
            func.coalesce(cls.area,0).label('crop_area'),
            func.coalesce(cls.is_approved, None).label('is_approved'),
            func.coalesce(cls.bt_id, bt_id).label('bt_id'),
            Crop.crop_name
        ).outerjoin(
            cls, 
            (Crop.id==cls.crop_id) &
            (cls.bt_id==bt_id)
        ).order_by(desc(func.coalesce(cls.area,0).label('crop_area')))

        results = query.all()

        if results:
            json_data = [{
                'id': index + 1,
                'table_id': item.table_id,
                'bt_id': item.bt_id,
                'crop_id': item.crop_id,
                'crop_area': item.crop_area,
                'crop_name': item.crop_name,
                'is_approved': item.is_approved
                } for index,item in enumerate(results)]
            return json_data        
        else:
            return None
    
    @classmethod
    def get_block_crop_data(cls, bt_id):
        query = db.session.query(
            cls.area,
            cls.crop_id,
            Crop.crop_name,
            cls.is_approved,
            Crop.coefficient
        ).join(Crop, Crop.id==cls.crop_id            
        ).filter(cls.bt_id == bt_id
        ).order_by(desc(cls.area * Crop.coefficient))

        results = query.all()

        if results:
            json_data = [{
                'entity_id': item.crop_id,
                'entity_count': item.area,
                'entity_name': item.crop_name,
                'is_approved': item.is_approved,
                'coefficient': item.coefficient
            } for item in results]
            return json_data
        else:
            return None

    @classmethod    
    def get_by_id(cls, id):
        return cls.query.filter(cls.id==id).first()
    
    @classmethod
    def check_duplicate(cls, crop_id, bt_id):
        return cls.query.filter(cls.crop_id==crop_id, cls.bt_id==bt_id).first()
   
    
    def save_to_db(self):
        duplicate_item = self.check_duplicate(self.crop_id, self.bt_id)
        if duplicate_item:
            duplicate_item.area = self.area
            duplicate_item.created_by = self.created_by
            duplicate_item.created_on = BlockCrop.get_current_time()
            duplicate_item.is_approved = self.is_approved
            duplicate_item.update_db()
        else:
            db.session.add(self)
        db.session.commit()

    def update_db(self):
        db.session.commit()
    
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
    