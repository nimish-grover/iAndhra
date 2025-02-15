from zoneinfo import ZoneInfo
from sqlalchemy import and_, case, func
from app.db import db
from datetime import datetime, timezone

from app.models.block_crops import BlockCrop
from app.models.block_ground import BlockGround
from app.models.block_industries import BlockIndustry
from app.models.block_livestocks import BlockLivestock
from app.models.block_lulc import BlockLULC
from app.models.block_pop import BlockPop
from app.models.block_rainfall import BlockRainfall
from app.models.block_surface import BlockWaterbody
from app.models.block_transfer import BlockWaterTransfer


class BlockTerritory(db.Model):
    __tablename__ = 'block_territory'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    state_id = db.Column(db.ForeignKey('states.id'), nullable=False)
    district_id = db.Column(db.ForeignKey('districts.id'), nullable=False)
    block_id = db.Column(db.ForeignKey('blocks.id'), nullable=False)
    panchayat_id = db.Column(db.ForeignKey('panchayats.id'), nullable=True)
    village_id = db.Column(db.ForeignKey('villages.id'),unique=True, nullable=True)
    is_approved = db.Column(db.Boolean, nullable=False, default=False)
    created_on = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(ZoneInfo('Asia/Kolkata')))
    
    state = db.relationship('State', backref=db.backref('block_territory', lazy='dynamic'))
    district = db.relationship('District', backref=db.backref('block_territory', lazy='dynamic'))
    block = db.relationship('Block', backref=db.backref('block_territory', lazy='dynamic'))
    # panchayat = db.relationship('Panchayat', backref=db.backref('block_territory', lazy='dynamic'))
    village = db.relationship('Village', backref=db.backref('block_territory', lazy='dynamic'))
    
    def __init__(self,state_id,district_id, block_id,panchayat_id,village_id ,is_approved=False):
        self.state_id = state_id
        self.district_id = district_id
        self.block_id = block_id
        self.panchayat_id = panchayat_id
        self.village_id = village_id
        self.is_approved = is_approved
  
    def json(self):
        return {
            "id":self.id,
            "state_id":self.state_id,
            "district_id":self.district_id,
            "block_id":self.block_id,
            "panchayat_id":self.panchayat_id,
            "village_id":self.village_id,
            "is_approved":self.is_approved,
            "created_on":self.created_on    
        }
    
    @classmethod
    def get_by_block_id(cls,_block_id):
        query = cls.query.filter_by(block_id=_block_id).first()
        if query:
            return query.json()
        else:
            return None
    
    @classmethod
    def get_bt_id(cls,village_id,panchayat_id,block_id, district_id, state_id):
        return db.session.query(cls.id).filter(
                cls.block_id == block_id,
                cls.district_id == district_id,
                cls.state_id == state_id,
                cls.panchayat_id == panchayat_id,
                cls.village_id == village_id
            ).scalar()
    
    
    @classmethod
    def get_all(cls):
        query=cls.query.order_by(cls.id.desc())
        return query

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def delete_from_db(cls,_id):
        user = cls.query.filter_by(id=_id).first()
        db.session.delete(user)
        db.session.commit()

    def commit_db():
        db.session.commit()

    @classmethod
    def update_db(cls,data,_id):
        user = cls.query.filter_by(id=_id).update(data)
        db.session.commit()
    @classmethod
    def get_status_by_bt_id(cls, bt_id):
        query = db.session.query(
            func.coalesce(func.max(case((BlockPop.is_approved == 'True', 1), else_=0)), 0).label('population'),
            func.coalesce(func.max(case((BlockLivestock.is_approved == 'True', 1), else_=0)), 0).label('livestock'),
            func.coalesce(func.max(case((BlockCrop.is_approved == 'True', 1), else_=0)), 0).label('crop'),
            func.coalesce(func.max(case((BlockIndustry.is_approved == 'True', 1), else_=0)), 0).label('industry'),
            func.coalesce(func.max(case((BlockWaterbody.is_approved == 'True', 1), else_=0)), 0).label('surface'),
            func.coalesce(func.max(case((BlockGround.is_approved == 'True', 1), else_=0)), 0).label('ground'),
            func.coalesce(func.max(case((BlockLULC.is_approved == 'True', 1), else_=0)), 0).label('lulc'),
            func.coalesce(func.max(case((BlockRainfall.is_approved == 'True', 1), else_=0)), 0).label('rainfall'),
            func.coalesce(func.max(case((BlockWaterTransfer.is_approved == 'True', 1), else_=0)), 0).label('water_transfer')
        ).select_from(BlockTerritory
        ).join(
            BlockPop, BlockPop.bt_id == BlockTerritory.id, isouter=True
        ).join(
            BlockCrop, BlockCrop.bt_id == BlockTerritory.id, isouter=True
        ).join(
            BlockLivestock, BlockLivestock.bt_id == BlockTerritory.id, isouter=True
        ).join(
            BlockIndustry, BlockIndustry.bt_id == BlockTerritory.id, isouter=True
        ).join(
            BlockWaterbody, BlockWaterbody.bt_id == BlockTerritory.id, isouter=True
        ).join(
            BlockGround, BlockGround.bt_id == BlockTerritory.id, isouter=True
        ).join(
            BlockLULC, BlockLULC.bt_id == BlockTerritory.id, isouter=True
        ).join(
            BlockWaterTransfer, BlockWaterTransfer.bt_id == BlockTerritory.id, isouter=True
        ).join(
            BlockRainfall, BlockRainfall.bt_id == BlockTerritory.id, isouter=True
        ).filter(
            BlockTerritory.id == bt_id
        ).all()
        
        return query 