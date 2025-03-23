from app.db import db


class BlockTransferType(db.Model):
    __tablename__ = "block_transfer_types"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True,)
    transfer_type = db.Column(db.String(100),unique=True, nullable=False)
    remarks = db.Column(db.String(200))

    def __init__(self, transfer_type, remarks):
        self.transfer_type = transfer_type
        self.remarks = remarks

    def json(self):
        return {
            'id': self.id,
            'transfer_type': self.transfer_type,
            'remarks': self.remarks
        }
    
    @classmethod
    def get_all(cls):
        results = cls.query.all()
        if results:
            return results
        else:
            data = cls.json_data["transfer_types"]
            for item in data:
                block_transfer_type = BlockTransferType(transfer_type=item)
                db.session.add(block_transfer_type)
            db.session.commit()
            return cls.query.all()

    json_data = {
        "transfer_types":['inward','outward']
    }