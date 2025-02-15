from sqlalchemy import func
from app.db import db
# from app.models.territory import TerritoryJoin

class Village(db.Model):
    __tablename__ = 'villages'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    state_lgd_code = db.Column(db.Integer, db.ForeignKey('states.lgd_code'), nullable=False)
    district_lgd_code = db.Column(db.Integer, db.ForeignKey('districts.lgd_code'), nullable=False)
    lgd_code = db.Column(db.Integer, unique=True, nullable=False)
    village_name = db.Column(db.String(255), nullable=True)
    panchayat_lgd_code = db.Column(db.Integer, db.ForeignKey('panchayats.lgd_code'), nullable=True)
    block_lgd_code = db.Column(db.Integer, db.ForeignKey('blocks.lgd_code'), nullable=False)

    # Relationships (if needed)
    state = db.relationship('State', backref=db.backref('villages', lazy='dynamic'))
    district = db.relationship('District', backref=db.backref('villages', lazy='dynamic'))
    block = db.relationship('Block',backref=db.backref('villages', lazy='dynamic'))
    panchayat = db.relationship('Panchayat', backref=db.backref('villages', lazy='dynamic'))

    # territory = db.relationship('TerritoryJoin', backref=db.backref('villages', lazy=True), uselist=False, foreign_keys="[TerritoryJoin.village_id]")

    def __init__(self, state_lgd_code, panchayat_lgd_code,district_lgd_code, lgd_code, village_name, census_code):
        """
        Initialize the Village instance with the provided attributes.
        """
        self.state_lgd_code = state_lgd_code
        self.panchayat_lgd_code = panchayat_lgd_code
        self.district_lgd_code = district_lgd_code
        self.lgd_code = lgd_code
        self.village_name = village_name
        self.census_code = census_code

    def __repr__(self):
        """
        Provides a string representation of the Village instance.
        """
        return (
            f"<Village(id={self.id}, state_lgd_code={self.state_lgd_code}, "
            f"district_lgd_code={self.district_lgd_code}, lgd_code={self.lgd_code}, "
            f"village_name='{self.village_name}', census_code={self.census_code})>"
        )

    def json(self):
        """
        Returns a JSON serializable dictionary representation of the Village instance.
        """
        return {
            "id": self.id,
            "state_lgd_code": self.state_lgd_code,
            "panchayat_lgd_code": self.panchayat_lgd_code,
            "district_lgd_code": self.district_lgd_code,
            "lgd_code": self.lgd_code,
            "village_name": self.village_name,
            "census_code": self.census_code
        }
    
    # @classmethod
    # def get_villages_number_by_block(cls,block_id,district_id):
    #     query = db.session.query(
    #         func.count(Village.id).label("village_count")
    #         ).join(TerritoryJoin, TerritoryJoin.village_id == Village.id
    #         ).filter(
    #             TerritoryJoin.block_id == block_id,
    #             TerritoryJoin.district_id == district_id
    #         )
    #     results = query.first()
    #     return results.village_count
