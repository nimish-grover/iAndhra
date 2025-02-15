from sqlalchemy import Numeric, func
from app.db import db
from app.models.block_lulc import BlockLULC
from app.models.block_territory import BlockTerritory
from app.models.blocks import Block
from app.models.districts import District
from app.models.panchayats import Panchayat
from app.models.villages import Village
from app.models.lulc import LULC
from app.models.territory import TerritoryJoin

class LULCCensus(db.Model):
    __tablename__ = 'lulc_census'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    lulc_id = db.Column(db.Integer, db.ForeignKey('lulc.id'), nullable=False)
    lulc_area = db.Column(db.Float, nullable=False)
    tj_id = db.Column(db.Integer, db.ForeignKey('territory_joins.id'), nullable=False)

    # Relationships
    lulc = db.relationship('LULC', backref=db.backref('lulc_census', lazy="dynamic"))
    territory_join = db.relationship('TerritoryJoin', backref=db.backref('lulc_census', lazy="dynamic"))

    def __init__(self, lulc_id, lulc_area, tj_id):
        self.lulc_id = lulc_id
        self.lulc_area = lulc_area
        self.tj_id = tj_id

    def __repr__(self):
        return f"<LULCCensus(id={self.id}, lulc_id={self.lulc_id}, lulc_area={self.lulc_area}, tj_id={self.tj_id})>"

    def json(self):
        return {
            "id": self.id,
            "lulc_id": self.lulc_id,
            "lulc_area": self.lulc_area,
            "tj_id": self.tj_id
        }
    
    @classmethod
    def get_census_data_lulc(cls, village_id,panchayat_id,block_id, district_id):
        query = db.session.query(
                func.sum(cls.lulc_area).label('catchment_area'),
                LULC.catchment,
                ).join(TerritoryJoin, TerritoryJoin.id==cls.tj_id
                ).join(LULC, LULC.id==cls.lulc_id
                ).join(Block, Block.id == TerritoryJoin.block_id
                ).join(District, District.id==TerritoryJoin.district_id
                ).join(Panchayat, Panchayat.id==TerritoryJoin.panchayat_id
                ).join(Village, Village.id==TerritoryJoin.village_id
                ).filter(
                    Block.id == block_id, 
                    District.id == district_id,
                    Panchayat.id == panchayat_id,
                    Village.id == village_id
                ).group_by(LULC.catchment)
        
        results = query.all()

        if results:
            json_data = [{
                'catchment': row.catchment,
                'catchment_area': row.catchment_area
            } for row in results]
            return json_data
        return None
    
    @classmethod
    def get_lulc_by_block(cls, block_id, district_id):
        block_lulc_subquery = db.session.query(
                func.sum(BlockLULC.area).label("catchment_area"),
                BlockLULC.lulc_id.label("lulc_id"),
                ).join(BlockTerritory, BlockTerritory.id == BlockLULC.bt_id
                ).join(Block, Block.id == BlockTerritory.block_id
                ).filter(Block.id == block_id
                ).group_by(BlockLULC.lulc_id
                ).subquery()

        # Subquery for `lulc_census`
        lulc_census_subquery = db.session.query(
                func.sum(LULCCensus.lulc_area).label("catchment_area"),
                LULCCensus.lulc_id.label("lulc_id"),
                ).join(TerritoryJoin, TerritoryJoin.id == LULCCensus.tj_id
                ).join(Block, Block.id == TerritoryJoin.block_id
                ).filter(Block.id == block_id
                ).group_by(LULCCensus.lulc_id
                ).subquery()

        # Main query
        query = db.session.query(
                LULC.catchment.label("catchment"),
                func.coalesce(
                    func.sum(block_lulc_subquery.c.catchment_area),
                    func.sum(lulc_census_subquery.c.catchment_area),
                    0
                ).label("catchment_area"),
                ).outerjoin(block_lulc_subquery, block_lulc_subquery.c.lulc_id == LULC.id
                ).outerjoin(lulc_census_subquery, lulc_census_subquery.c.lulc_id == LULC.id
                ).group_by(LULC.catchment)
        
        results = query.all()

        if results:
            json_data = [{
                'catchment': row.catchment,
                'catchment_area': row.catchment_area
            } for row in results]
            return json_data
        return None
    
    @classmethod 
    def get_lulc(cls,village_id,panchayat_id,block_id,district_id):
        query = db.session.query(
            func.round(func.sum(LULCCensus.lulc_area).cast(Numeric), 2).label('lulc_area'),
            LULC.id,
            LULC.display_name
        ).join(TerritoryJoin, TerritoryJoin.id == LULCCensus.tj_id
        ).join(LULC, LULC.id == LULCCensus.lulc_id
        ).join(Block, Block.id == TerritoryJoin.block_id
        ).join(District, District.id == TerritoryJoin.district_id
        ).join(Panchayat,Panchayat.id == TerritoryJoin.panchayat_id
        ).join(Village, Village.id == TerritoryJoin.village_id
        ).filter(Block.id == block_id, District.id == district_id,Panchayat.id == panchayat_id, Village.id == village_id
        ).group_by(LULC.id)
        
        results = query.all()
        
        if results:
            json_data = [{
                'lulc_id':row.id,
                'lulc_area':row.lulc_area
            } for row in results]
            return json_data
        return None