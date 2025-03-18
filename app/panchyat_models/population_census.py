from sqlalchemy import func
from app.db import db
from app.models import Population, TerritoryJoin
from app.models.block_pop import BlockPop
from app.models.block_territory import BlockTerritory
from app.models.blocks import Block
from app.models.districts import District

class PopulationCensus(db.Model):
    __tablename__ = 'population_census'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    population_id = db.Column(db.Integer, db.ForeignKey('population.id'), nullable=False)
    population_count = db.Column(db.Integer, nullable=False)
    territory_id = db.Column(db.Integer, db.ForeignKey('territory_joins.id'), nullable=False)

    # Relationships
    population = db.relationship('Population', backref=db.backref('population_census', lazy="dynamic"))
    territory = db.relationship('TerritoryJoin', backref=db.backref('population_census', lazy="dynamic"))

    def __init__(self, population_id, population_count, territory_id):
        """
        Initialize the PopulationCensus instance with the provided attributes.
        """
        self.population_id = population_id
        self.population_count = population_count
        self.territory_id = territory_id

    def __repr__(self):
        """
        Provides a string representation of the PopulationCensus instance.
        """
        return (f"<PopulationCensus(id={self.id}, population_id={self.population_id}, "
                f"population_count={self.population_count}, territory_id={self.territory_id})>")

    def json(self):
        """
        Returns a JSON serializable dictionary representation of the PopulationCensus instance.
        """
        return {
            "id": self.id,
            "population_id": self.population_id,
            "population_count": self.population_count,
            "territory_id": self.territory_id
        }
    @classmethod
    def get_census_data_population(cls,panchayat_id,block_id, district_id):
        query = db.session.query(
            func.sum(PopulationCensus.population_count).label("population_count"),
            Population.id,
            Population.display_name
            ).join(TerritoryJoin, TerritoryJoin.id == PopulationCensus.territory_id
            ).join(Population, Population.id == PopulationCensus.population_id
            ).filter(
                TerritoryJoin.block_id == block_id,
                TerritoryJoin.district_id == district_id,
                TerritoryJoin.panchayat_id == panchayat_id,
                Population.id.in_([2, 3]) # 2 = 'male', 3 = 'female'
            ).group_by(
                TerritoryJoin.block_id,
                TerritoryJoin.district_id,
                Population.id,
                Population.display_name,
                Population.population_type
            )
        results = query.all()

        if results:
            result = [
                {
                    "entity_value": row.population_count,
                    "entity_id": row.id,
                    "entity_name": row.display_name
                }
                for row in results
            ]
            return result
        else:
            return None  

    @classmethod
    def get_population_by_block(cls, block_id, district_id):
        subquery_bp = db.session.query(
                BlockPop.population_id.label("population_id"),
                func.sum(BlockPop.count).label("total_count")
            ).join(BlockTerritory, BlockPop.bt_id == BlockTerritory.id
            ).join(Block, BlockTerritory.block_id == Block.id
            #).filter(Block.lgd_code == block_lgd)
            ).filter(
                Block.id == block_id,
                District.id == district_id
            ).group_by(BlockPop.population_id
            ).subquery()

        # Subquery for population_census
        subquery_pc = db.session.query(
                PopulationCensus.population_id.label("population_id"),
                func.sum(PopulationCensus.population_count).label("total_count")
            ).join(TerritoryJoin, PopulationCensus.territory_id == TerritoryJoin.id
            ).join(Block, TerritoryJoin.block_id == Block.id
            #).filter(Block.lgd_code == block_lgd)
            ).filter(
                Block.id == block_id,
                District.id == district_id
            ).group_by(PopulationCensus.population_id
            ).subquery()

        # Main query
        query = db.session.query(
                Population.display_name.label("display_name"),
                Population.id.label("id"),
                func.coalesce(
                    subquery_bp.c.total_count,
                    subquery_pc.c.total_count,
                    0
                ).label("population_count")
            ).outerjoin(subquery_bp, subquery_bp.c.population_id == Population.id
            ).outerjoin(subquery_pc, subquery_pc.c.population_id == Population.id
            ).filter(Population.id.in_([2, 3])
            ).order_by(Population.id)
        
        results = query.all()

        if results:
            result = [
                {
                    "entity_value": row.population_count,
                    "entity_id": row.id,
                    "entity_name": row.display_name
                }
                for row in results
            ]
            return result
        else:
            return None
