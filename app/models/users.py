from flask_login import UserMixin
from sqlalchemy import case, func
from app.db import db
from passlib.hash import pbkdf2_sha256

from app.models.districts import District
from app.models.blocks import Block
from app.models.panchayats import Panchayat
from sqlalchemy.dialects.postgresql import ARRAY


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(300))
    district_id = db.Column(db.Integer, db.ForeignKey("districts.id"), nullable=False)
    block_id = db.Column(db.Integer, db.ForeignKey("blocks.id"), nullable=False)
    # panchayat_id = db.Column(db.Integer, db.ForeignKey("panchayats.id"), nullable=False)
    panchayat_id = db.Column(ARRAY(db.Integer))

    isActive = db.Column(db.Boolean, nullable=False, default=False)
    isAdmin = db.Column(db.Boolean, nullable=False, default=False)
    district = db.relationship("District", backref=db.backref('districts', lazy='dynamic'))
    block = db.relationship("Block", backref=db.backref('blocks', lazy='dynamic'))
    # panchayat = db.relationship("Panchayat", backref=db.backref('panchayats', lazy='dynamic'))
    
    def __init__(self, username, password, district_id,block_id,panchayat_id, isActive, isAdmin):
        self.username = username
        self.password = password
        self.isActive = isActive
        self.isAdmin = isAdmin
        self.district_id = district_id
        self.block_id = block_id
        self.panchayat_id = panchayat_id

    def json(self):
        return {
            'id': self.id,
            'username': self.username,
            'isActive': self.isActive,
            'isAdmin': self.isAdmin,
            'district_id': self.district_id,
            'block_id': self.block_id,
            'panchayat_id': self.panchayat_id
        }
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    
    def update_db(self):
        db.session.commit()

    def set_password(self, password):
        self.password = pbkdf2_sha256.hash(password)
    
    def check_password(self, password):
        return pbkdf2_sha256.verify(password, self.password)

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()
    
    @classmethod
    def get_panchayat_id_by_block(cls,block_id,user_id=None):
        query = db.session.query(func.unnest(cls.panchayat_id)).filter(cls.block_id == block_id)
        if user_id:
            query = query.filter(cls.id == user_id)
        result = query.all()
        result = [item[0] for item in result]
        return result
    
    @classmethod
    def get_all(cls):
        query = db.session.query(
            cls.id, 
            cls.username,
            cls.isActive,
            Panchayat.panchayat_name,
            District.district_name,
            District.short_name,
            Block.block_name
        ).join(
            District,District.id==cls.district_id
        ).join(
            Block, Block.id==cls.block_id
        ).join(
            Panchayat, Panchayat.id==cls.panchayat_id
        ).order_by(District.district_name,Block.block_name,Panchayat.panchayat_name)
        
        results = query.all()
        
        if results:
            json_data = [{
                'id': item.id,
                'username': item.username,
                'isActive': item.isActive,
                'district_short_name':item.short_name,
                'block_name': item.block_name,
                'district_name':item.district_name,
                'panchayat_name':item.panchayat_name
            } for item in results]
            return json_data
        return None
    
    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter(cls.id==id).first()
    
    @classmethod
    def get_active_count(cls):
        counts = db.session.query(
            func.count(case((cls.isActive == 'True', 1))).label('active_users'),
            func.count(case((cls.isActive == 'False', 1))).label('inactive_users')
        ).one()

        return {
            'active_users': counts.active_users,
            'inactive_users': counts.inactive_users
        }
    