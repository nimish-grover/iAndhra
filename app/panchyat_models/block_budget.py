import datetime
from zoneinfo import ZoneInfo
from app import db


class BlockBudget(db.Model):
    def get_current_time():
        return datetime.now(ZoneInfo('Asia/Kolkata'))
    
    __tablename__ = "block_budgets"

    id = db.Column(db.Integer, primary_key=True)
    bt_id = db.Column(db.Integer, db.ForeignKey('block_territory.id'), nullable=False)
    entity_id = db.Column(db.Integer, db.ForeignKey('budget_entities.id'), nullable=False)
    value = db.Column(db.Float, nullable=False, default=0)
    is_approved = db.Column(db.Boolean, nullable=False, default=False)
    created_on = db.Column(db.DateTime, default=get_current_time)

    entity = db.relationship('BlockEntity', backref=db.backref('block_budgets', lazy='dynamic'))
    territory = db.relationship('BlockTerritory', backref=db.backref('block_budgets', lazy='dynamic'))

    def __init__(self, bt_id, entity_id, value, is_approved, created_on):
        self.bt_id = bt_id
        self.entity_id = entity_id
        self.value = value
        self.is_approved = is_approved
        self.created_on = created_on

    def json(self):
        return {
            'bt_id': self.bt_id,
            'entity_id': self.entity_id,
            'value': self.value,
            'is_approved': self.is_approved,
            'created_on': self.created_on
        }
    
    def save_to_db(self):
        duplicate_item = self.check_duplicate(self.entity_id,self.entity_id,self.bt_id)
        if duplicate_item:
            duplicate_item.value = self.value
            duplicate_item.created_on = BlockBudget.get_current_time()
            duplicate_item.is_approved = self.is_approved
            duplicate_item.update_db()
        else:
            db.session.add(self)
        db.session.commit()
        
    def update_db(self):
        db.session.commit()
    
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()