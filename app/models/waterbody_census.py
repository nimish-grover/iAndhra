from sqlalchemy import func
from app.db import db
from app.models.block_surface import BlockWaterbody
from app.models.block_territory import BlockTerritory
from app.models.blocks import Block
from app.models.territory import TerritoryJoin
from app.models.waterbody import WaterbodyType

class WaterbodyCensus(db.Model):
    __tablename__ = 'waterbodies_census'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    spread_area = db.Column(db.Float, nullable=False)
    storage_capacity = db.Column(db.Float, nullable=False)
    max_depth = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.String(80), nullable=True)
    latitude = db.Column(db.String(80), nullable=True)
    waterbody_id = db.Column(db.Integer, db.ForeignKey("waterbody_types.id"), nullable=False)
    village_code = db.Column(db.Integer, db.ForeignKey("villages.lgd_code"), nullable=False)
    # block_code = db.Column(db.Integer, db.ForeignKey("blocks.lgd_code"), nullable=True)
    district_code = db.Column(db.Integer, db.ForeignKey("districts.lgd_code"), nullable=False)
    tj_id = db.Column(db.Integer, db.ForeignKey("territory_joins.id"), nullable=False)

    village = db.relationship("Village", backref=db.backref("waterbodies_census", lazy="dynamic"))
    # block = db.relationship("Block", backref=db.backref("waterbodies_census", lazy="dynamic"))
    district = db.relationship("District", backref=db.backref("waterbodies_census", lazy="dynamic"))
    territory_join = db.relationship("TerritoryJoin", backref=db.backref("waterbodies_census", lazy="dynamic"))
    waterbody_type = db.relationship("WaterbodyType", backref=db.backref("waterbodies_census", lazy="dynamic"))

    def __init__(self, spread_area, storage_capacity, max_depth, longitude=None, latitude=None, 
                 waterbody_id=None, village_code=None, block_code=None, district_code=None, 
                 tj_id=None):
        """
        Initialize the WaterbodiesCensus instance with the provided attributes.
        """
        self.spread_area = spread_area
        self.storage_capacity = storage_capacity
        self.max_depth = max_depth
        self.longitude = longitude
        self.latitude = latitude
        self.waterbody_id = waterbody_id
        self.village_code = village_code
        self.block_code = block_code
        self.district_code = district_code
        self.tj_id = tj_id

    def __repr__(self):
        """
        Provides a string representation of the WaterbodiesCensus instance.
        """
        return (f"<WaterbodiesCensus(id={self.id}, spread_area={self.spread_area}, "
                f"storage_capacity={self.storage_capacity}, max_depth={self.max_depth}, "
                f"longitude='{self.longitude}', latitude='{self.latitude}', "
                f"waterbody_id={self.waterbody_id}, village_code={self.village_code}, "
                f"block_code={self.block_code}, district_code={self.district_code}, "
                f"village_id={self.tj_id})>")

    def json(self):
        """
        Returns a JSON serializable dictionary representation of the WaterbodiesCensus instance.
        """
        return {
            "id": self.id,
            "spread_area": self.spread_area,
            "storage_capacity": self.storage_capacity,
            "max_depth": self.max_depth,
            "longitude": self.longitude,
            "latitude": self.latitude,
            "waterbody_id": self.waterbody_id,
            "village_code": self.village_code,
            "block_code": self.block_code,
            "district_code": self.district_code,
            "tj_id": self.tj_id
        }
    
    @classmethod
    def get_census_data_waterbody(cls, villageid,panchayat_id,block_id, district_id):
        query = db.session.query(
                func.sum(cls.storage_capacity).label('storage_capacity'),
                func.count(cls.waterbody_id).label('waterbody_count'),
                WaterbodyType.id.label('waterbody_id'),
                WaterbodyType.waterbody_name
            ).join(WaterbodyType, WaterbodyType.id==cls.waterbody_id
            ).join(TerritoryJoin, TerritoryJoin.id==cls.tj_id
            ).filter(
                TerritoryJoin.block_id == block_id,
                TerritoryJoin.district_id == district_id,
                TerritoryJoin.village_id == villageid,
                TerritoryJoin.panchayat_id == panchayat_id
            ).group_by(
                WaterbodyType.id,WaterbodyType.waterbody_name
            )
        results = query.all()
        if results:
            json_data = [{'entity_id':row.waterbody_id,
                          'entity_name': row.waterbody_name,
                          'entity_count': row.waterbody_count,
                          'entity_value': row.storage_capacity}
                         for row in results]
            return json_data
        return None
    
    @classmethod
    def get_waterbody_by_block(cls, block_id, district_id):
        block_waterbodies_subquery = db.session.query(
                BlockWaterbody.wb_type_id.label("waterbody_id"),
                func.sum(BlockWaterbody.storage).label("total_storage"),
                func.sum(BlockWaterbody.count).label("total_count")
                ).join(BlockTerritory, BlockTerritory.id == BlockWaterbody.bt_id
                ).join(Block, Block.id == BlockTerritory.block_id
                ).filter(Block.id == block_id
                ).group_by(BlockWaterbody.wb_type_id
                ).subquery()

        # Subquery for waterbodies_census
        waterbodies_census_subquery = db.session.query(
                WaterbodyCensus.waterbody_id.label("waterbody_id"),
                func.sum(WaterbodyCensus.storage_capacity).label("total_storage"),
                func.count(WaterbodyCensus.waterbody_id).label("total_count")
                ).join(TerritoryJoin, TerritoryJoin.id == WaterbodyCensus.tj_id
                ).join(Block, Block.id == TerritoryJoin.block_id
                ).filter(Block.id == block_id
                ).group_by(WaterbodyCensus.waterbody_id
                ).subquery()

        # Main query
        query = db.session.query(
                WaterbodyType.waterbody_name,
                WaterbodyType.id.label("waterbody_id"),
                func.coalesce(block_waterbodies_subquery.c.total_storage, waterbodies_census_subquery.c.total_storage, 0).label("storage_capacity"),
                func.coalesce(block_waterbodies_subquery.c.total_count, waterbodies_census_subquery.c.total_count, 0).label("waterbody_count"),
                ).outerjoin(block_waterbodies_subquery, block_waterbodies_subquery.c.waterbody_id == WaterbodyType.id
                ).outerjoin(waterbodies_census_subquery, waterbodies_census_subquery.c.waterbody_id == WaterbodyType.id)

        results = query.all()
        if results:
            json_data = [{'entity_id':row.waterbody_id,
                          'entity_name': row.waterbody_name,
                          'entity_count': row.waterbody_count,
                          'entity_value': row.storage_capacity}
                         for row in results]
            return json_data
        return None
