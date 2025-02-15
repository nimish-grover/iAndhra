from app.db import db


class BlockTransferSector(db.Model):
    __tablename__ = "block_transfer_sectors"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True,)
    sector = db.Column(db.String(100), unique=True, nullable=False)
    remarks = db.Column(db.String(200))

    def __init__(self, sector, remarks):
        self.sector = sector
        self.remarks = remarks

    def json(self):
        return {
            'id': self.id,
            'sector': self.sector,
            'remarks': self.remarks
        }
    
    @classmethod
    def get_all(cls):
        results = cls.query.all()
        if results:
            return results
        else:
            data = cls.json_data["transfer_sectors"]
            for item in data:
                block_transfer_type = BlockTransferSector(sector=item)
                db.session.add(block_transfer_type)
            db.session.commit()
            return cls.query.all()

    json_data = {
        "transfer_sectors":['drinking','irrigation','industry']
    }