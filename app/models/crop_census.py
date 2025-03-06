from sqlalchemy import func
from app.db import db
from app.models.block_crops import BlockCrop
from app.models.block_territory import BlockTerritory
from app.models.blocks import Block
from app.models.crops import Crop
from app.models.territory import TerritoryJoin

class CropCensus(db.Model):
    __tablename__ = 'crop_census'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    territory_id = db.Column(db.Integer, db.ForeignKey('territory_joins.id'), nullable=False)
    panchayat_lgd_code = db.Column(db.Integer, db.ForeignKey('panchayats.lgd_code'), nullable=False)
    crop_id = db.Column(db.Integer, db.ForeignKey('crops.id'), nullable=False)
    crop_area = db.Column(db.Float, nullable=False)


    # Relationships
    territory = db.relationship('TerritoryJoin', backref=db.backref('crop_census', lazy="dynamic"))
    panchayat = db.relationship('Panchayat', backref=db.backref('crop_census', lazy="dynamic"))
    crop = db.relationship('Crop', backref=db.backref('crop_census', lazy="dynamic"))

    def __init__(self, territory_id, panchayat_lgd_code, crop_id, crop_area):
        """
        Initialize the CropCensus instance with the provided attributes.
        """
        self.territory_id = territory_id
        self.panchayat_lgd_code = panchayat_lgd_code
        self.crop_id = crop_id
        self.crop_area = crop_area


    def __repr__(self):
        """
        Provides a string representation of the CropCensus instance.
        """
        return (f"<CropCensus(id={self.id}, territory_id={self.territory_id}, "
                f"panchayat_lgd_code={self.panchayat_lgd_code}, crop_id={self.crop_id}, "
                f"season='{self.season}', crop_area={self.crop_area}, production={self.production}, "
                f"crop_yield={self.crop_yield})>")

    def json(self):
        """
        Returns a JSON serializable dictionary representation of the CropCensus instance.
        """
        return {
            "id": self.id,
            "territory_id": self.territory_id,
            "panchayat_lgd_code": self.panchayat_lgd_code,
            "crop_id": self.crop_id,
            "crop_area": self.crop_area,
        }
    
    @classmethod
    def get_census_data_crops(cls,village_id,panchayat_id, block_id, district_id):
        query = db.session.query(
            func.sum(cls.crop_area).label('crop_area'),
            Crop.id.label('crop_id'),
            Crop.coefficient,
            Crop.crop_name
        ).join(Crop, Crop.id == cls.crop_id
        ).join(TerritoryJoin, TerritoryJoin.id == cls.territory_id
        ).filter(
            TerritoryJoin.block_id==block_id,
            TerritoryJoin.district_id==district_id,
            TerritoryJoin.panchayat_id==panchayat_id,
            TerritoryJoin.village_id==village_id
        ).group_by(
            Crop.id,Crop.coefficient,Crop.crop_name
        )
        results = query.all()
        if results:
            json_data = [{
                        'entity_id':row.crop_id,
                        'entity_value':row.crop_area, 
                        'entity_name':row.crop_name,
                        'coefficient':row.coefficient }
                          for row in results]
            return json_data
        return None
    
    @classmethod
    def get_crops_by_block(cls, block_id, district_id):
        block_crops_subquery = (
            db.session.query(
                BlockCrop.crop_id.label("crop_id"),
                func.sum(BlockCrop.area).label("total_area")
            )
            .join(BlockTerritory, BlockTerritory.id == BlockCrop.bt_id)
            .join(Block, Block.id == BlockTerritory.block_id)
            .filter(Block.id == block_id)
            .group_by(BlockCrop.crop_id)
            .subquery()
        )

        # Subquery for crop_census
        crop_census_subquery = db.session.query(
                CropCensus.crop_id.label("crop_id"),
                func.sum(CropCensus.crop_area).label("total_area")
                ).join(TerritoryJoin, TerritoryJoin.id == CropCensus.territory_id
                ).join(Block, Block.id == TerritoryJoin.block_id\
                ).filter(Block.id == block_id
                ).group_by(CropCensus.crop_id
                ).subquery()

        # Main query
        query = db.session.query(
                Crop.crop_name,
                Crop.id.label("crop_id"),
                Crop.coefficient,
                func.coalesce(block_crops_subquery.c.total_area, crop_census_subquery.c.total_area, 0).label("crop_area"),
                ).outerjoin(block_crops_subquery, block_crops_subquery.c.crop_id == Crop.id
                ).outerjoin(crop_census_subquery, crop_census_subquery.c.crop_id == Crop.id)
            
        results = query.all()
        if results:
            json_data = [{
                        'entity_id':row.crop_id,
                        'entity_value':row.crop_area, 
                        'entity_name':row.crop_name,
                        'coefficient':row.coefficient }
                          for row in results]
            return json_data
        return None