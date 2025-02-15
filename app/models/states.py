from flask import url_for
from sqlalchemy import case, func
from app.db import db
# from app.models.block_crops import BlockCrop
# from app.models.block_ground import BlockGround
# from app.models.block_industries import BlockIndustry
# from app.models.block_livestocks import BlockLivestock
# from app.models.block_lulc import BlockLULC
# from app.models.block_pop import BlockPop
# from app.models.block_rainfall import BlockRainfall
# from app.models.block_surface import BlockWaterbody
# from app.models.block_territory import BlockTerritory
# from app.models.block_transfer import BlockWaterTransfer
from app.models.blocks import Block
from app.models.districts import District

class State(db.Model):
    __tablename__ = 'states'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    lgd_code = db.Column(db.Integer, unique=True, nullable=True)
    state_name = db.Column(db.String(255), nullable=True)
    census_code = db.Column(db.Integer, nullable=True)
    is_state = db.Column(db.Boolean, nullable=True, default=True)
    short_name = db.Column(db.String(10), nullable=True)

    def __init__(self, lgd_code, state_name=None, census_code=None, is_state=None, short_name=None):
        self.lgd_code = lgd_code
        self.state_name = state_name
        self.census_code = census_code
        self.is_state = is_state
        self.short_name = short_name

    def __repr__(self):
        return f"<State(id={self.id}, lgd_code={self.lgd_code}, state_name={self.state_name})>"

    def json(self):
        return {
            "id": self.id,
            "lgd_code": self.lgd_code,
            "state_name": self.state_name,
            "census_code": self.census_code,
            "is_state": self.is_state,
            "short_name": self.short_name
        }
    
    @classmethod
    def get_states_by_id(cls, state_id):
        results = cls.query.filter_by(id=state_id).all()
        if results:
            json_data = [{'tj_id':0,'id':item.id,'name':item.state_name,'code':item.lgd_code} for item in results]
            return json_data
        else:
            return None
        
    # @classmethod
    # def get_all_states_status(cls):
    #     block_lgd_codes = [4876, 1740, 7130, 539, 172, 3209, 6050, 7047, 3784, 3837, 3979, 4010, 4027, 4628, 624, 762, 781, 2157, 6255, 6287, 6468, 5250, 823, 951, 994]
    #     district_lgd_codes = [745, 196, 641, 72, 20, 338, 563, 9, 434, 398, 431, 426, 405, 500, 92, 115, 112, 227, 583, 596, 610, 721, 129, 119, 132]
    #     query = (
    #         db.session.query(
    #             State.state_name,
    #             State.id.label("state_id"),
    #             State.short_name.label("state_short_name"),
    #             District.district_name,
    #             District.id.label("district_id"),
    #             Block.block_name,
    #             Block.id.label("block_id"),
    #             func.coalesce(BlockTerritory.id, 0).label("bt_id"),
    #             func.coalesce(
    #                 func.max(case((BlockPop.is_approved == 'True', 1), else_=0)), 0
    #             ).label("population"),
    #             func.coalesce(
    #                 func.max(case((BlockLivestock.is_approved == 'True', 1), else_=0)), 0
    #             ).label("livestock"),
    #             func.coalesce(
    #                 func.max(case((BlockCrop.is_approved == 'True', 1), else_=0)), 0
    #             ).label("crop"),
    #             func.coalesce(
    #                 func.max(case((BlockIndustry.is_approved == 'True', 1), else_=0)), 0
    #             ).label("industry"),
    #             func.coalesce(
    #                 func.max(case((BlockWaterbody.is_approved == 'True', 1), else_=0)), 0
    #             ).label("surface"),
    #             func.coalesce(
    #                 func.max(case((BlockGround.is_approved == 'True', 1), else_=0)), 0
    #             ).label("ground"),
    #             func.coalesce(
    #                 func.max(case((BlockLULC.is_approved == 'True', 1), else_=0)), 0
    #             ).label("lulc"),
    #             func.coalesce(
    #                 func.max(case((BlockRainfall.is_approved == 'True', 1), else_=0)), 0
    #             ).label("rainfall"),
    #             func.coalesce(
    #                 func.max(case((BlockWaterTransfer.is_approved == 'True', 1), else_=0)), 0
    #             ).label("water_transfer"),
    #         )
    #         .outerjoin(District, District.state_lgd_code == State.lgd_code)
    #         .outerjoin(Block, Block.district_lgd_code == District.lgd_code)
    #         .outerjoin(BlockTerritory, BlockTerritory.block_id == Block.id)
    #         .outerjoin(BlockPop, BlockPop.bt_id == BlockTerritory.id)
    #         .outerjoin(BlockCrop, BlockCrop.bt_id == BlockTerritory.id)
    #         .outerjoin(BlockLivestock, BlockLivestock.bt_id == BlockTerritory.id)
    #         .outerjoin(BlockIndustry, BlockIndustry.bt_id == BlockTerritory.id)
    #         .outerjoin(BlockWaterbody, BlockWaterbody.bt_id == BlockTerritory.id)
    #         .outerjoin(BlockGround, BlockGround.bt_id == BlockTerritory.id)
    #         .outerjoin(BlockLULC, BlockLULC.bt_id == BlockTerritory.id)
    #         .outerjoin(BlockRainfall, BlockRainfall.bt_id == BlockTerritory.id)
    #         .outerjoin(BlockWaterTransfer, BlockWaterTransfer.bt_id == BlockTerritory.id)
    #         .filter(Block.lgd_code.in_(block_lgd_codes))
    #         .filter(District.lgd_code.in_(district_lgd_codes))
    #         .group_by(
    #             State.state_name,
    #             District.district_name,
    #             Block.block_name,
    #             BlockTerritory.id,
    #             State.id,
    #             District.id,
    #             Block.id,
    #             State.short_name,
    #         )
    #         .order_by(State.state_name)
    #     )
    #     results = query.all()
    #     results_dict = [row._asdict() for row in results]
    #     for row in results_dict:
    #         status_count = 0 
    #         category = ['population','livestock','crop','industry','surface','ground','lulc','rainfall','water_transfer']
    #         for item in category:
    #             if row[item]:
    #                 status_count += 1
    #         if status_count < 9 and status_count > 0:
    #             row['completed'] = 11*status_count
    #         elif status_count == 9:
    #             row['completed'] = 100
    #         else:
    #             row['completed'] = 0 
    #         row['url'] = url_for('desktop.human')
    #     sorted_dict = sorted(results_dict, key=lambda x: x["completed"])
    #     for idx, item in enumerate(sorted_dict):
    #         item['id'] = idx + 1
    #     return sorted_dict


