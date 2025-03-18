
from app.db import db

class District(db.Model):
    __tablename__ = 'districts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    state_lgd_code = db.Column(db.Integer, db.ForeignKey('states.lgd_code'), nullable=False)
    lgd_code = db.Column(db.Integer, unique=True, nullable=False)
    district_name = db.Column(db.String(255), nullable=True)
    short_name = db.Column(db.String(10), nullable=True)

    # census_code = db.Column(db.Integer, nullable=False)

    # Relationship to State
    state = db.relationship("State", backref=db.backref("districts", lazy="dynamic"))

    def __init__(self, state_lgd_code, lgd_code, district_name=None,short_name=None):
        self.state_lgd_code = state_lgd_code
        self.lgd_code = lgd_code
        self.district_name = district_name
        self.short_name = short_name
        

    def __repr__(self):
        return f"<District(id={self.id}, state_lgd_code={self.state_lgd_code}, lgd_code={self.lgd_code})>"

    def json(self):
        return {
            "id": self.id,
            "state_lgd_code": self.state_lgd_code,
            "lgd_code": self.lgd_code,
            "district_name": self.district_name,
            "short_name":self.short_name
        }
        
    @classmethod
    def get_districts_by_id(cls, district_id):
        results = cls.query.filter_by(id=district_id).all()
        if results:
            json_data = [{'tj_id':0,'id':item.id,'name':item.district_name,'code':item.lgd_code} for item in results]
            return json_data
        else:
            return None
        
    @classmethod
    def get_short_name(cls,district_id):
        results = cls.query.filter_by(id=district_id).all()
        if results:
            short_name = [item.short_name for item in results]
            return short_name[0]