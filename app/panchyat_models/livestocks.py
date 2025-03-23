from app.db import db

class Livestock(db.Model):
    __tablename__ = 'livestocks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    livestock_name = db.Column(db.String(100), unique=True, nullable=True)
    category = db.Column(db.String(100), nullable=True)
    coefficient = db.Column(db.Float, nullable=False)
    remarks = db.Column(db.String(300), nullable=True)

    def __init__(self, livestock_name=None, category=None, coefficient=None, remarks=None):
        self.livestock_name = livestock_name
        self.category = category
        self.coefficient = coefficient
        self.remarks = remarks

    def __repr__(self):
        return f"<Livestock(id={self.id}, livestock_name={self.livestock_name}, category={self.category}, coefficient={self.coefficient})>"

    def json(self):
        return {
            "id": self.id,
            "livestock_name": self.livestock_name,
            "category": self.category,
            "coefficient": self.coefficient,
            "remarks": self.remarks
        }

    @classmethod
    def get_all_livestocks(cls):
        query = db.session.query(cls.id,cls.livestock_name).all()
        if query:
            json_data = [{'livestock_id':item.id,'livestock_name':item.livestock_name} for item in query]
            return json_data