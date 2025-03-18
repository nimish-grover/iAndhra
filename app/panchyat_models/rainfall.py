# from datetime import datetime
from sqlalchemy import Numeric, alias, and_, cast, func
from app.db import db
from app.models.block_rainfall import BlockRainfall
from app.models.block_territory import BlockTerritory
from app.models.blocks import Block

class Rainfall(db.Model):
    __tablename__ = 'rainfall_data'

    id = db.Column(db.Integer, primary_key=True)
    month_year = db.Column(db.DateTime,nullable=False)
    normal = db.Column(db.Float(53), nullable=False)
    actual = db.Column(db.Float(53), nullable=False)
    district_id = db.Column(db.ForeignKey('districts.id'), nullable=False)
    
    district = db.relationship('District', backref=db.backref("rainfall_data", lazy="dynamic"))

    def __init__(self, month_year, normal, actual, district_id):
        self.month_year = month_year
        self.normal = normal
        self.actual = actual
        self.district_id = district_id

    def json(self):
        return {
            'id': self.id,
            'month_year': self.month_year,
            'normal': self.normal,
            'actual': self.actual,
            'district_id': self.district_id 
        }
    
    @classmethod
    def get_census_data_rainfall(cls, district_id):
        results = db.session.query(
                        cls.actual,
                        cls.normal,
                        func.to_char(cls.month_year, 'Mon-YY').label("month"),
                        cls.month_year
                    ).filter(cls.district_id == district_id
                    ).order_by(cls.month_year
                    ).all()
                
        if results:
            result = [{'month':result[2],'actual':result[0],'normal':result[1],'date':result[3]} for result in results]
        else: 
            result = [{'month':0,'actual':0,'normal':0}]
        return result
 
    @classmethod
    def get_monthwise_rainfall(cls, block_id, district_id):
        block_rainfall_subquery = db.session.query(
                func.to_char(BlockRainfall.month_year, 'FMMon-YY').label('date'),
                func.round(func.sum(BlockRainfall.actual).cast(Numeric), 2).label('actual'),
                func.round(func.sum(BlockRainfall.normal).cast(Numeric), 2).label('normal'),
            ).join(BlockTerritory, BlockTerritory.id == BlockRainfall.bt_id
            ).join(Block, Block.id == BlockTerritory.block_id
            ).filter(Block.id == block_id
            ).group_by(func.to_char(BlockRainfall.month_year, 'FMMon-YY')
            ).subquery()

        # Subquery for rainfall_data
        rainfall_data_subquery = db.session.query(
                func.to_char(Rainfall.observation_date, 'FMMon-YY').label('date'),
                func.round(func.sum(Rainfall.actual).cast(Numeric), 2).label('actual'),
                func.round(func.sum(Rainfall.normal).cast(Numeric), 2).label('normal'),            
            ).filter(Rainfall.district_id == district_id
            ).group_by(func.to_char(Rainfall.observation_date, 'FMMon-YY')
            ).subquery()

        # Main query
        query = db.session.query(
                func.to_char(Rainfall.observation_date, 'FMMon-YY').label('month_year'),
                func.coalesce(block_rainfall_subquery.c.actual, rainfall_data_subquery.c.actual, 0).label('actual'),
                func.coalesce(block_rainfall_subquery.c.normal, rainfall_data_subquery.c.normal, 0).label('normal'),
            ).outerjoin(
                block_rainfall_subquery,
                func.to_char(Rainfall.observation_date, 'FMMon-YY') == block_rainfall_subquery.c.date,
            ).outerjoin(
                rainfall_data_subquery,
                func.to_char(Rainfall.observation_date, 'FMMon-YY') == rainfall_data_subquery.c.date,
            ).group_by(
                func.to_char(Rainfall.observation_date, 'FMMon-YY'),
                block_rainfall_subquery.c.actual,
                block_rainfall_subquery.c.normal,
                rainfall_data_subquery.c.actual,
                rainfall_data_subquery.c.normal,
            ).order_by(func.min(Rainfall.observation_date))

        results = query.all()
        if results:
            result = [{'month':result[0],'actual':result[1],'normal':result[2]} for result in results]
        else: 
            result = [{'month':0,'actual':0,'normal':0}]
        return result
        # '''
        # SELECT
        # TO_CHAR(observation_date, 'Mon-YYYY') AS observation,
        # SUM(actual) AS actual
        # FROM
        #     rainfall_data
        # WHERE
        #     EXTRACT(YEAR FROM observation_date) = 2023 and district_id = 639
        # GROUP BY
        #     observation, EXTRACT(MONTH FROM observation_date), EXTRACT(YEAR FROM observation_date)
        # ORDER BY
        #     EXTRACT(YEAR FROM observation_date), EXTRACT(MONTH FROM observation_date);
        # '''
       