from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import func
from app.db import db
from app.models.lulc import LULC


class BlockLULC(db.Model):
    def get_current_time():
        return datetime.now(ZoneInfo('Asia/Kolkata'))
    
    __tablename__ = 'block_lulc'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    area = db.Column(db.Float, nullable=False)
    bt_id = db.Column(db.ForeignKey('block_territory.id'), nullable=False)
    is_approved = db.Column(db.Boolean, nullable=False, default=False)
    created_on = db.Column(db.DateTime, default=get_current_time)
    lulc_id = db.Column(db.ForeignKey('lulc.id'), nullable=False)
    created_by = db.Column(db.ForeignKey('users.id'), nullable=False)
    
    users = db.relationship('User', backref=db.backref('block_lulc', lazy='dynamic'))
    lulc = db.relationship('LULC', backref=db.backref('block_lulc', lazy='dynamic'))
    block_territory = db.relationship('BlockTerritory', backref=db.backref('block_lulc', lazy='dynamic'))

    
    def __init__(self,lulc_id,area,bt_id,is_approved,created_by):
        self.lulc_id = lulc_id
        self.area = area
        self.bt_id = bt_id
        self.is_approved = is_approved
        self.created_by = created_by
        
    def json(self):
        return {
            "id":self.id,
            "area":self.area,
            "lulc_id":self.lulc_id,
            "bt_id":self.bt_id,
            "is_approved":self.is_approved,
            "created_by":self.created_by,
            "creatd_on":self.created_on
        }
    
    @classmethod    
    def get_by_id(cls, id):
        return cls.query.filter(cls.id==id).first()

    @classmethod
    def get_by_bt_id(cls, bt_id):
        query = db.session.query(
            cls.id, 
            func.coalesce(cls.area,0).label('area'),
            LULC.id.label('lulc_id'),
            LULC.display_name,
            func.coalesce(cls.bt_id, bt_id).label("bt_id"),
            func.coalesce(cls.is_approved, None).label('is_approved')
        ).outerjoin(
            cls,
            (LULC.id==cls.lulc_id) &
            (cls.bt_id == bt_id) 
        ).filter(~LULC.id.in_([15]
        )).order_by(LULC.id)

        results = query.all()
        if results:
            json_data = [{
                'id': index + 1,
                'table_id': row.id,
                'area': row.area,
                'lulc_id': row.lulc_id,
                'lulc_name':row.display_name,
                'bt_id': row.bt_id,
                'is_approved': row.is_approved
                } for index,row in enumerate(results)]
            return json_data

        return None
    
    @classmethod
    def get_block_lulc_data(cls,bt_id):
        query = (
            db.session.query(
                LULC.catchment,
                func.sum(cls.area).label('catchment_area'),
                cls.is_approved
            )
            .join(LULC, LULC.id == cls.lulc_id)
            .filter(cls.bt_id == bt_id)
            .group_by(LULC.catchment, cls.is_approved)
        )

        # Execute the query
        results = query.all()
        if results:
            json_data = [{
                'catchment': row.catchment,
                'catchment_area': row.catchment_area,
                'is_approved': row.is_approved
            } for row in results]
            return json_data
        return None
    
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
            duplicate_item.created_on = BlockLULC.get_current_time()
        else:
            db.session.add(self)
        db.session.commit()

    def update_db(self):
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()