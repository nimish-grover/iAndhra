from app.db import db


class BlockCategory(db.Model):
    __tablename__ = 'block_category'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(255), nullable=True)


    def __init__(self, name):
        self.name = name


    def json(self):
        return {
            "id": self.id,
            "name": self.name
        }
        
        
    @classmethod
    def get_category_id(cls,category):
        query = db.session.query(cls.id).filter(cls.name == category).scalar()
        return query 
    
    @classmethod
    def get_category_name(cls,id):
        query = db.session.query(cls.name).filter(cls.id == id).first()
        return query[0]