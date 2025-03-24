from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import case, desc, func
from app.db import db
from app.models.industries import Industry


class BlockIndustry(db.Model):
    def get_current_time():
        return datetime.now(ZoneInfo('Asia/Kolkata'))
    
    __tablename__ = 'block_industries'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    industry_id = db.Column(db.Integer, db.ForeignKey('industries.id'), nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    count = db.Column(db.Integer, nullable = False)
    allocation = db.Column(db.Float, nullable=False)
    bt_id = db.Column(db.Integer, db.ForeignKey('block_territory.id'), nullable=False)
    is_approved = db.Column(db.Boolean, nullable=False, default=False)
    created_on = db.Column(db.DateTime, default=get_current_time)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    users = db.relationship('User', backref=db.backref('block_industries', lazy='dynamic'))
    block_territory = db.relationship('BlockTerritory', backref=db.backref('block_industries', lazy='dynamic'))
    industries = db.relationship('Industry', backref=db.backref('block_industries', lazy='dynamic'))
    
    def __init__(self,industry_id,allocation,unit,count,bt_id,is_approved,created_by):
        self.industry_id = industry_id
        self.allocation = allocation
        self.unit = unit
        self.count = count
        self.bt_id = bt_id
        self.is_approved = is_approved
        self.created_by = created_by
        
    def json(self):
        return {
            "id":self.id,
            "industry_id":self.industry_id,
            "unit":self.unit,
            "allocation":self.allocation,
            "is_approved":self.is_approved,
            "bt_id":self.bt_id,
            "created_by":self.created_by,
            "creatd_on":self.created_on
        }
    
    @classmethod
    def get_by_bt_id(cls, bt_id):
        query = db.session.query(
            func.coalesce(cls.id,0).label('table_id'),
            func.coalesce(cls.bt_id,bt_id).label('bt_id'),
            Industry.id.label('industry_id'),
            Industry.industry_sector,
            cls.unit,
            func.coalesce(cls.is_approved, None).label('is_approved'),
            func.coalesce(func.sum(cls.allocation),0).label('annual_allocation'),
            func.coalesce(func.sum(cls.count),0).label('industry_count')
            # func.coalesce(
            #     func.sum(case((cls.bt_id == bt_id, cls.allocation),else_=0)),0).label("allocation")
        ).outerjoin( 
                    cls, 
                    (Industry.id == cls.industry_id) & 
                    (cls.bt_id==bt_id)
        ).group_by(cls.id, Industry.id,Industry.industry_sector, cls.unit
        ).order_by(Industry.industry_sector)

        results = query.all()

        if results:
            json_data = [{
                'id':index + 1,
                'table_id': item.table_id,
                'bt_id': item.bt_id,
                'unit': item.unit,
                'is_approved': item.is_approved,
                'industry_id':item.industry_id,
                'industry_sector':item.industry_sector,
                'allocation':item.annual_allocation,
                'count':item.industry_count
            } for index, item in enumerate(results)]
            return json_data
        return None
    
    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter(cls.id==id).first()
    
    @classmethod
    def get_industry_by_block(cls, bt_id):
        query = db.session.query(
        Industry.id,
        Industry.industry_sector,
        func.coalesce(
            func.sum(cls.allocation),0
        ).label('allocation'),
        func.coalesce(
            func.sum(cls.count),0
        ).label('count')
        ).outerjoin( 
                    cls, 
                    (Industry.id == cls.industry_id) & 
                    (cls.bt_id==bt_id)
        ).group_by(Industry.id,Industry.industry_sector
        ).order_by(desc(func.coalesce(
            func.sum(cls.allocation),0
        ).label('allocation')))

        results = query.all()

        if results:
            # json_data = [result for result in results]
            json_data = [{
                        'entity_id':row.id,
                        'entity_value':row.count, 
                        'entity_name':row.industry_sector,
                        'entity_consumption':row.allocation
                        } 
                        for row in results]
            return json_data
        else:
            return None
    
    @classmethod
    def get_block_industry_data(cls,bt_id=0):
        query = db.session.query(
        Industry.id,
        Industry.industry_sector,
        cls.is_approved,
        func.coalesce(cls.allocation,0).label('allocation'),
        func.coalesce(cls.count, 0).label('count')
        ).outerjoin( 
                    cls, 
                    (Industry.id == cls.industry_id) & 
                    (cls.bt_id==bt_id)
        ).order_by(desc(func.coalesce(cls.allocation,0)
        ).label('allocation'))

        results = query.all()

        if results:
            json_data = [{
                        'entity_id':row.id,
                        'entity_count':row.count, 
                        'entity_name':row.industry_sector,
                        'entity_consumption':row.allocation,
                        'is_approved': row.is_approved } 
                        for row in results]
            return json_data
        else:
            return None

    @classmethod
    def check_duplicate(cls, industry_id, bt_id):
        return cls.query.filter(cls.industry_id==industry_id, cls.bt_id==bt_id).first()
    
    def update_db(self):
        db.session.commit()

    def save_to_db(self):
        duplicate_item = self.check_duplicate(self.industry_id, self.bt_id)
        if duplicate_item:
            duplicate_item.allocation = self.allocation
            duplicate_item.count = self.count
            duplicate_item.unit = self.unit
            duplicate_item.created_on = BlockIndustry.get_current_time()
            duplicate_item.created_by = self.created_by
            duplicate_item.is_approved = self.is_approved
        else:
            db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()