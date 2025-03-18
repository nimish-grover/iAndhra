
from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import func
from app.db import db


class BlockRainfall(db.Model):
    def get_current_time():
        return datetime.now(ZoneInfo('Asia/Kolkata'))
    
    __tablename__ = 'block_rainfall'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    normal = db.Column(db.Float, nullable=False)
    actual = db.Column(db.Float, nullable=False)
    month_year = db.Column(db.DateTime, nullable=False)
    bt_id = db.Column(db.ForeignKey('block_territory.id'), nullable=False)
    is_approved = db.Column(db.Boolean, nullable=False, default=False)
    created_on = db.Column(db.DateTime, default=get_current_time)
    created_by = db.Column(db.ForeignKey('users.id'), nullable=False)
    
    users = db.relationship('User', backref=db.backref('block_rainfall', lazy='dynamic'))
    block_territory = db.relationship('BlockTerritory', backref=db.backref('block_rainfall', lazy='dynamic'))

    def __init__(self,normal,actual,bt_id,is_approved,created_by,month_year):
        self.normal = normal
        self.actual = actual
        self.month_year = month_year
        self.bt_id = bt_id
        self.is_approved = is_approved
        self.created_by = created_by
        
    def json(self):
        return {
            "id":self.id,
            "actual":self.actual,
            "normal":self.normal,
            "month_year":self.month_year,
            "bt_id":self.bt_id,
            "is_approved":self.is_approved,
            "created_by":self.created_by,
            "created_on":self.created_on
        }
    
    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter(cls.id==id).first()
    
    @classmethod
    def get_rainfall_data(cls, bt_id):
        query = (
            db.session.query(
                cls.month_year,
                func.round(func.sum(cls.actual).cast(db.Numeric), 2).label('actual'),
                func.round(func.sum(cls.normal).cast(db.Numeric), 2).label('normal'),
                cls.is_approved
            )
            .filter(cls.bt_id == bt_id)
            .group_by(cls.month_year,cls.is_approved)
            .order_by(func.min(cls.month_year))
        )

        # Execute the query
        results = query.all()

        if results:
            json_data = [{
                'month': row.month_year.strftime('%b-%y'),
                'actual': row.actual,
                'normal': row.normal,
                'is_approved': row.is_approved
                } for row in results]
            return json_data
        return None
        
    @classmethod
    def get_by_bt_id(cls, bt_id):
        query = db.session.query(
            cls.id, 
            func.to_char(cls.month_year, 'Mon-YY').label("month"),
            func.coalesce(cls.actual,0).label('actual'),
            func.coalesce(cls.normal,0).label('normal'),
            func.coalesce(cls.bt_id,bt_id).label("bt_id"),
            cls.is_approved
        ).filter(
            cls.bt_id == bt_id
        ).order_by(cls.month_year)

        results = query.all()

        if results:
            json_data = [{
                'id': index + 1,
                'table_id': row.id,
                'month_year': row.month,
                'actual': row.actual,
                'normal': row.normal,
                'bt_id': row.bt_id,
                'is_approved': row.is_approved
                } for index,row in enumerate(results)]
            return json_data

        return None

    @classmethod
    def get_all(cls):
        query=cls.query.order_by(cls.id.desc())
        return query
    
    @classmethod
    def check_duplicate(cls, month_year, bt_id):
        return cls.query.filter(cls.month_year==month_year, cls.bt_id==bt_id).first()

    def update_db(self):
        db.session.commit()

    def save_to_db(self):
        duplicate_item = self.check_duplicate(self.month_year, self.bt_id)
        if duplicate_item:
            duplicate_item.actual = self.actual
            duplicate_item.created_by = self.created_by
            duplicate_item.is_approved = self.is_approved
            duplicate_item.created_on = BlockRainfall.get_current_time()
        else:
            db.session.add(self)
        db.session.commit()