from app.db import db


class Industry(db.Model):

    __tablename__ = 'industries'

    id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    industry_sector = db.Column(db.String(200), nullable=False, unique=True)

    def __init__(self, industry_sector):
        self.industry_sector = industry_sector

    def json(self):
        return {
            'id': self.id,
            'industry_sector' : self.industry_sector
        }
    
    @classmethod
    def get_all_industries(cls):
        results = cls.query.all()

        if results:
            return results
        else:
            data = cls.json_data["industries"]
            for industry_name in data:
                industry = Industry(industry_sector=industry_name)
                db.session.add(industry)
            db.session.commit()
            return cls.query.all()

    json_data = {
        "industries": [
            "Aerospace and Aviation",
            "Agriculture",
            "Apparel Made Ups & Home Furnishing",
            "Automotive",
            "Beauty & Wellness",
            "Banking Financial Services and Insurance",
            "Capital Goods",
            "Cement",
            "Construction",
            "Electronics",
            "Food Industry",
            "Furniture & Fittings",
            "Gem & Jewellery",
            "Handicrafts and Carpet",
            "Healthcare",
            "Hydrocarbon",
            "Indian Iron and Steel",
            "Infrastructure Equipment",
            "Instrumentation Automation",
            "IT ITeS",
            "Leather",
            "Life Sciences",
            "Logistics",
            "Media & Entertainment",
            "Power",
            "Retailers Association's",
            "Rubber Chemical & Petrochemical",
            "Green Industries",
            "Mining",
            "Sports Physical Education Fitness & Leisure",
            "Telecom",
            "Textile",
            "Tourism and Hospitality",
            "Water Management & Plumbing"
        ]
    }
    
    @classmethod
    def get_all_industries(cls):
        query = db.session.query(cls.id,cls.industry_sector).all()
        if query:
            json_data = [{'industry_id':item.id,'industry_name':item.industry_sector} for item in query]
            return json_data