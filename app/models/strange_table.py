from sqlalchemy import func, literal
from app.db import db


class StrangeTable(db.Model):
    __tablename__ = "strange_table"

    id=db.Column(db.Integer, primary_key=True)
    rainfall_in_inches=db.Column(db.Integer)
    rainfall_in_mm = db.Column(db.Float)
    good_runoff = db.Column(db.Float)
    average_runoff = db.Column(db.Float)
    bad_runoff = db.Column(db.Float)

    def __init__(self, rainfall, good, average, bad):
        self.rainfall_in_mm = rainfall
        self.good_runoff = good
        self.average_runoff = average
        self.bad_runoff = bad

    def json(self):
        return {
            'rainfall': self.rainfall_in_mm,
            'good': self.good_runoff,
            'bad': self.bad_runoff,
            'average': self.average_runoff
        }

    @classmethod
    def get_runoff_by_rainfall(cls, rainfall_in_mm):
        # Subquery to calculate the minimum rainfall_in_mm >= 20
        subquery_min_rainfall = db.session.query(
            func.min(StrangeTable.rainfall_in_mm)
        ).filter(
            StrangeTable.rainfall_in_mm >= rainfall_in_mm
        ).scalar_subquery()

        # Subquery to fetch runoff_data
        query = db.session.query(
                StrangeTable.rainfall_in_mm.label("rainfall_in_mm"),
                StrangeTable.good_runoff.label("good_runoff"),
                StrangeTable.average_runoff.label("average_runoff"),
                StrangeTable.bad_runoff.label("bad_runoff"),
            ).filter(StrangeTable.rainfall_in_mm == subquery_min_rainfall)

        # Execute the query
        results = query.all()

        if results:
            json_data = [{
                'good': row.good_runoff,
                'average': row.average_runoff,
                'bad': row.bad_runoff,
                'rainfall_in_mm': row.rainfall_in_mm
            } for row in results]
            return json_data

        return None        
    