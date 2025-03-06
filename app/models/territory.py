from sqlalchemy import func
from app.db import db
from app.models.states import State
from app.models.districts import District
from app.models.blocks import Block
from app.models.panchayats import Panchayat
from app.models.villages import Village

class TerritoryJoin(db.Model):
    __tablename__ = 'territory_joins'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True, nullable=False)
    state_id = db.Column(db.Integer, db.ForeignKey('states.id'), nullable=False)
    district_id = db.Column(db.Integer, db.ForeignKey('districts.id'), nullable=False)
    block_id = db.Column(db.Integer, db.ForeignKey('blocks.id'), nullable=True)
    panchayat_id = db.Column(db.Integer, db.ForeignKey('panchayats.id'), nullable=True)
    # village_id = db.Column(db.Integer, db.ForeignKey('villages.id'), nullable=False)

    # Relationships
    state = db.relationship("State", backref=db.backref("territory_joins", lazy="dynamic"))
    district = db.relationship("District", backref=db.backref("territory_joins", lazy="dynamic"))
    block = db.relationship("Block", backref=db.backref("territory_joins", lazy="dynamic"))
    panchayat = db.relationship("Panchayat", backref=db.backref("territory_joins", lazy="dynamic"))
    # village = db.relationship("Village", backref=db.backref("territory_joins", lazy="dynamic"))

    def __init__(self, state_id, district_id, block_id=None, panchayat_id=None, rec_status=0):
        self.state_id = state_id
        self.district_id = district_id
        self.panchayat_id = panchayat_id
        self.block_id = block_id
        self.rec_status = rec_status

    def __repr__(self):
        return (f"<TerritoryJoin(id={self.id}, state_id={self.state_id}, "
                f"district_id={self.district_id}, block_id={self.block_id}, "
                f"rec_status={self.rec_status})>")

    def json(self):
        return {
            "id": self.id,
            "state_id": self.state_id,
            "district_id": self.district_id,
            "block_id": self.block_id,
            "panchayat_id": self.panchayat_id,
            "rec_status": self.rec_status
        }
    @classmethod
    def get_districts(cls, state_id=2):
        results = db.session.query(
            cls.id.label('tj_id'),
            District.id.label('id'),
            District.district_name.label('name'),
            District.lgd_code.label('code')
        ).join(District, District.id==cls.district_id
        ).filter(cls.state_id==state_id
        ).order_by(District.district_name
        ).distinct(District.id, District.district_name, District.lgd_code
        ).all()

        if results:
            json_data = [{'tj_id':item[0],'id':item[1],'name':item[2],'code':item[3]} for item in results]
            return json_data
        else:
            return None
    
    @classmethod
    def get_aspirational_states(cls):
        results = db.session.query(
            cls.id.label('tj_id'),
            State.id.label('id'),
            State.state_name.label('name'),
            State.lgd_code.label('code')
        ).join(State, State.id==cls.state_id
        ).join(District, District.id==cls.district_id
        ).filter(District.lgd_code.in_([745,196,641,72,20,338,563,9,434,398,431,426,405,500,92,115,112,227,583,596,610,721,129,119,132])
        ).order_by(State.state_name
        ).distinct(State.id, State.state_name, State.lgd_code
        ).all()
        if results:
            return results
        else:
            return None 
        
    @classmethod
    def get_aspirational_districts(cls, state_id):
        results = db.session.query(
            cls.id.label('tj_id'),
            District.id.label('id'),
            District.district_name.label('name'),
            District.lgd_code.label('code')
        ).join(District, District.id==cls.district_id
        ).filter(District.lgd_code.in_([745,196,641,72,20,338,563,9,434,398,431,426,405,500,92,115,112,227,583,596,610,721,129,119,132]), cls.state_id==state_id
        ).order_by(District.district_name
        ).distinct(District.id, District.district_name, District.lgd_code
        ).all()

        if results:
            json_data = [{'tj_id':item[0],'id':item[1],'name':item[2],'code':item[3]} for item in results]
            return json_data
        else:
            return None
        
    
    @classmethod
    def get_blocks(cls, district_id):
        results = db.session.query(
            cls.id.label('tj_id'),
            Block.id.label('id'),
            Block.block_name.label('name'),
            Block.lgd_code.label('code')
        ).join(Block, Block.id==cls.block_id
        ).filter(cls.district_id==district_id
        ).order_by(Block.block_name
        ).distinct(Block.id, Block.block_name, Block.lgd_code
        ).all()

        if results:
            json_data = [{'tj_id':item[0],'id':item[1],'name':item[2],'code':item[3]} for item in results]
            return json_data
        else:
            return None
        
    @classmethod
    def get_panchayats(cls, block_id):
        results = db.session.query(
            cls.id.label('tj_id'),
            Panchayat.id.label('id'),
            Panchayat.panchayat_name.label('name'),
            Panchayat.lgd_code.label('code')
        ).join(Panchayat, Panchayat.id==cls.panchayat_id
        ).filter(cls.block_id==block_id
        ).order_by(Panchayat.panchayat_name
        ).distinct(Panchayat.id, Panchayat.panchayat_name, Panchayat.lgd_code
        ).all()

        if results:
            json_data = [{'tj_id':item[0],'id':item[1],'name':item[2],'code':item[3]} for item in results]
            return json_data
        else:
            return None
    
    @classmethod
    def get_villages(cls, panchayat_id):
        results = db.session.query(
            cls.id.label('tj_id'),
            Village.id.label('id'),
            Village.village_name.label('name'),
            Village.lgd_code.label('code')
        ).join(Village, Village.id==cls.village_id
        ).filter(cls.panchayat_id==panchayat_id
        ).order_by(Village.village_name
        ).distinct(Village.id, Village.village_name, Village.lgd_code
        ).all()

        if results:
            json_data = [{'tj_id':item[0],'id':item[1],'name':item[2],'code':item[3]} for item in results]
            return json_data
        else:
            return None
    
    @classmethod
    def get_villages_number_by_panchayat(cls,panchayat_id,block_id,district_id):
        query = db.session.query(
            func.count(cls.id).label("village_count")
            ).filter(
                cls.panchayat_id == panchayat_id,
                cls.block_id == block_id,
                cls.district_id == district_id
            )
        results = query.first()
        return results.village_count