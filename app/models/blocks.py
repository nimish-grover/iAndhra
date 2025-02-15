from app.db import db

class Block(db.Model):
    __tablename__ = 'blocks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    state_lgd_code = db.Column(db.Integer, nullable=False)  # Note: Not a foreign key in the schema
    district_lgd_code = db.Column(db.Integer, db.ForeignKey('districts.lgd_code'), nullable=False)
    lgd_code = db.Column(db.Integer, nullable=False,unique=True)
    block_name = db.Column(db.String(255), nullable=True)

    __table_args__ = (
        db.UniqueConstraint('lgd_code', 'district_lgd_code', name='blocks_unique_lgd_code_district_lgd_code'),
    )

    # Relationship to District
    district = db.relationship("District", backref=db.backref("blocks", lazy="dynamic"))

    def __init__(self, state_lgd_code, district_lgd_code, lgd_code, block_name=None):
        self.state_lgd_code = state_lgd_code
        self.district_lgd_code = district_lgd_code
        self.lgd_code = lgd_code
        self.block_name = block_name

    def __repr__(self):
        return f"<Block(id={self.id}, lgd_code={self.lgd_code}, district_lgd_code={self.district_lgd_code})>"

    def json(self):
        return {
            "id": self.id,
            "state_lgd_code": self.state_lgd_code,
            "district_lgd_code": self.district_lgd_code,
            "lgd_code": self.lgd_code,
            "block_name": self.block_name
        }

