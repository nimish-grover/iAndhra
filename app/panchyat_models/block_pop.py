from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import func
from app.db import db
from app.models.population import Population


class BlockPop(db.Model):
    def get_current_time():
        return datetime.now(ZoneInfo("Asia/Kolkata"))
    
    __tablename__ = "block_pops"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    count = db.Column(db.Integer, nullable=False)
    created_on = db.Column(db.DateTime, default=get_current_time)
    bt_id = db.Column(db.Integer, db.ForeignKey('block_territory.id'), nullable=False)
    population_id = db.Column(db.Integer, db.ForeignKey('population.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_approved = db.Column(db.Boolean, nullable=False, default=False)

    block_territory = db.relationship('BlockTerritory', backref=db.backref('block_pops', lazy='dynamic'))
    population = db.relationship('Population', backref=db.backref('block_pops', lazy='dynamic'))
    user = db.relationship('User', backref=db.backref('block_pops', lazy='dynamic'))

    def __init__(self,population_id,count,bt_id,is_approved,created_by):
        self.population_id = population_id
        self.count = count
        self.bt_id = bt_id
        self.created_by = created_by
        self.is_approved = is_approved
        
    def json(self):
        return {
            "id":self.id,
            "population_id":self.population_id,
            "count":self.count,
            "bt_id":self.bt_id,
            "is_approved": self.is_approved,
            "created_by":self.created_by,
            "creatd_on":self.created_on
        }
    
    @classmethod
    def get_by_bt_id(cls, bt_id):
        query =  db.session.query(
            cls.id.label('table_id'),
            cls.population_id, 
            cls.count.label('count'),
            Population.population_type.label('category'),
            Population.display_name,
            cls.is_approved,
            func.coalesce(cls.bt_id,bt_id).label('bt_id')
        ).join(Population, 
               Population.id==cls.population_id).filter(cls.bt_id==bt_id)

        results = query.all()

        if results:
            json_data = [{
                'id': index + 1, 
                'table_id': item.table_id,
                'population_id':item.population_id, 
                'count': item.count, 
                'category': item.category, 
                'display_name':item.display_name, 
                'is_approved':item.is_approved,
                'bt_id': item.bt_id} 
                for index,item in enumerate(results)]
            return json_data
        else:
            return None
        
    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter(cls.id==id).first()
    
    @classmethod
    def get_block_population_data(cls, bt_id):
        query = db.session.query(
            cls.population_id,
            cls.count,
            Population.display_name,
            cls.is_approved    
        ).join(Population, Population.id==cls.population_id
        ).filter(cls.bt_id == bt_id)

        results = query.all()

        if results:
            json_data = [{
                'entity_id': item.population_id,
                'entity_count': item.count,
                'entity_name': item.display_name,
                'is_approved': item.is_approved
            } for item in results]
            return json_data
        else:
            return None
    
    @classmethod
    def check_duplicate(cls, population_id, bt_id):
        return cls.query.filter(cls.population_id==population_id, cls.bt_id==bt_id).first()

    def update_db(self):
        db.session.commit()

    def save_to_db(self):
        duplicate_item = self.check_duplicate(self.population_id, self.bt_id)
        if duplicate_item:
            duplicate_item.count=self.count
            duplicate_item.created_on = BlockPop.get_current_time()
            duplicate_item.created_by = self.created_by
            duplicate_item.is_approved = self.is_approved
            duplicate_item.update_db()
        else:
            db.session.add(self)
        db.session.commit()
    
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()