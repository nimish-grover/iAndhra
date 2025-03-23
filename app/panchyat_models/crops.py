from app.db import db

class Crop(db.Model):
    __tablename__ = 'crops'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    crop_name = db.Column(db.String(200), unique=True, nullable=False)
    coefficient = db.Column(db.Float, nullable=False)
    remarks = db.Column(db.String(300), nullable=True)

    def __init__(self, id, crop_name, coefficient, remarks=None):
        self.id = id
        self.crop_name = crop_name
        self.coefficient = coefficient
        self.remarks = remarks

    def __repr__(self):
        return f"<Crop(id={self.id}, crop_name={self.crop_name}, coefficient={self.coefficient})>"

    def json(self):
        return {
            "id": self.id,
            "crop_name": self.crop_name,
            "coefficient": self.coefficient,
            "remarks": self.remarks
        }
        
    @classmethod
    def get_all_crops(cls):
        query = db.session.query(cls.id,cls.crop_name).all()
        if query:
            json_data = [{'crop_id':item.id,'crop_name':item.crop_name} for item in query]
            return json_data