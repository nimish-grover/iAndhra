from app.db import db

class BudgetEntity(db.Model):
    __tablename__ = "budget_entities"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    source = db.Column(db.String(80), nullable=False)

    def __init__(self, name, source, table_name):
        self.name = name
        self.source = source

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'source': self.source
        }

