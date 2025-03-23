from app.db import db

class Panchayat(db.Model):
    __tablename__ = 'panchayats'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    state_lgd_code =     block_lgd_code = db.Column(db.Integer, db.ForeignKey('states.lgd_code'), nullable=False)
    district_lgd_code = db.Column(db.Integer, db.ForeignKey('districts.lgd_code'), nullable=False)
    block_lgd_code = db.Column(db.Integer, db.ForeignKey('blocks.lgd_code'), nullable=False)
    lgd_code = db.Column(db.Integer, nullable=False,unique=True)
    panchayat_name = db.Column(db.String(255), nullable=True)

    __table_args__ = (
        db.UniqueConstraint('lgd_code', 'block_lgd_code', name='panchayats_unique_lgd_code_block_lgd_code'),
    )

    # Relationship to District
    district = db.relationship("District", backref=db.backref("panchayats", lazy="dynamic"))
    block = db.relationship("Block", backref=db.backref("panchayats", lazy="dynamic"))
    state = db.relationship("State", backref=db.backref("panchayats", lazy="dynamic"))


    def __init__(self, state_lgd_code, district_lgd_code, lgd_code, block_lgd_code,panchayat_name=None):
        self.state_lgd_code = state_lgd_code
        self.district_lgd_code = district_lgd_code
        self.block_lgd_code = block_lgd_code
        self.lgd_code = lgd_code
        self.panchayat_name = panchayat_name

    def __repr__(self):
        return f"<Panchayat(id={self.id}, lgd_code={self.lgd_code}, district_lgd_code={self.district_lgd_code})>"

    def json(self):
        return {
            "id": self.id,
            "state_lgd_code": self.state_lgd_code,
            "district_lgd_code": self.district_lgd_code,
            "block_lgd_code": self.block_lgd_code,
            "lgd_code": self.lgd_code,
            "panchayat_name": self.panchayat_name
        }
        
    @classmethod
    def get_panchayat_name_by_id(cls,id):
        query = cls.query.filter_by(id=id).first()
        if query:
            return query.panchayat_name
        else:
            return None

