from app.db import db

class WaterbodyType(db.Model):
    __tablename__ = 'waterbody_types'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    waterbody_name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(100), nullable=True)

    def __init__(self, waterbody_name=None, description=""):
        """
        Initialize the Waterbody instance with the provided waterbody_name.
        """
        self.waterbody_name = waterbody_name
        self.description = description

    def __repr__(self):
        """
        Provides a string representation of the Waterbody instance.
        """
        return f"<Waterbody(id={self.id}, waterbody_name='{self.waterbody_name}', description='{self.description}')>"

    def json(self):
        """
        Returns a JSON serializable dictionary representation of the Waterbody instance.
        """
        return {
            "id": self.id,
            "waterbody_name": self.waterbody_name,
            "description": self.description
        }

    @classmethod
    def get_all_waterbodies(cls):
        query = db.session.query(cls.id,cls.waterbody_name).all()
        if query:
            json_data = [{'wb_type_id':item.id,'waterbody_name':item.waterbody_name} for item in query]
            return json_data