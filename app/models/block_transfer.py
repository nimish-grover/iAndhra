from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy import case, func, text
from app.db import db
from app.models.block_transfer_sector import BlockTransferSector
from app.models.block_transfer_type import BlockTransferType

class BlockWaterTransfer(db.Model):
    def get_current_time():
        return datetime.now(ZoneInfo('Asia/Kolkata'))

    __tablename__ = "block_water_transfers"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True,)
    transfer_quantity = db.Column(db.Float, nullable=False)
    transfer_type_id = db.Column(db.ForeignKey('block_transfer_types.id'), nullable=False)
    transfer_sector_id = db.Column(db.ForeignKey('block_transfer_sectors.id'), nullable=False)
    bt_id = db.Column(db.ForeignKey('block_territory.id'), nullable=False)
    created_by = db.Column(db.ForeignKey('users.id'))
    is_approved = db.Column(db.Boolean, default=False)
    created_on = db.Column(db.DateTime, default=get_current_time )

    transfer_type = db.relationship('BlockTransferType', backref = db.backref('block_water_transfers', lazy='dynamic'))
    transfer_sector = db.relationship('BlockTransferSector', backref = db.backref('block_water_transfers', lazy='dynamic'))

    def __init__(self, transfer_quantity, transfer_type_id, transfer_sector_id, bt_id, is_approved, created_by):
        self.transfer_quantity = transfer_quantity
        self.transfer_type_id = transfer_type_id
        self.transfer_sector_id = transfer_sector_id
        self.bt_id = bt_id
        self.created_by = created_by
        self.is_approved = is_approved

    def json(self):
        return {
            'id': self.id,
            'transfer_quantity': self.transfer_quantity,
            'transfer_type_id': self.transfer_type_id,
            'transfer_sector_id': self.transfer_sector_id
        }
    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter(cls.id==id).first()
    
    @classmethod
    def get_by_bt_id(cls, bt_id):
        query = db.session.query(
            BlockTransferType.id.label("type_id"),
            BlockTransferSector.id.label("sector_id"),
            func.concat(
                BlockTransferType.transfer_type,' (', BlockTransferSector.sector,')'
                ).label("water_transfer"),
            func.coalesce(BlockWaterTransfer.transfer_quantity,0).label("transfer_quantity"),
            cls.is_approved,
            func.coalesce(cls.id,None).label('table_id')
        ).select_from(BlockTransferType
        ).join(BlockTransferSector, text("1=1")
        ).outerjoin(
            cls,
            (BlockTransferType.id == BlockWaterTransfer.transfer_type_id) &
            (BlockTransferSector.id == BlockWaterTransfer.transfer_sector_id) & 
            (cls.bt_id==bt_id)
        ).order_by(BlockTransferType.id, BlockTransferSector.id)

        # Execute the query
        results = query.all()

        if results:
            json_data = [{
                'id': index + 1,
                'table_id': item.table_id,
                'bt_id': bt_id,
                'type_id':item.type_id,
                'sector_id':item.sector_id,
                'water_transfer':item.water_transfer,
                'quantity':item.transfer_quantity,
                'is_approved': item.is_approved
            } for index,item in enumerate(results)]
            return json_data
        return None
    
    @classmethod
    def get_water_transfer_by_block(cls, bt_id):
        query = db.session.query(
            func.concat(BlockTransferType.transfer_type, ' (', BlockTransferSector.sector, ')').label('transfer_type_sector'),
            func.coalesce(cls.transfer_quantity, 0).label('transfer_quantity'),
            cls.is_approved
            ).select_from(BlockTransferType
            ).join(BlockTransferSector, text("1=1")
            ).outerjoin(
                cls, 
                (BlockTransferType.id == cls.transfer_type_id) & 
                (BlockTransferSector.id == cls.transfer_sector_id) & 
                (cls.bt_id == bt_id)
            ).order_by('transfer_type_sector')

        results = query.all()

        if results:
            json_data = [{
                'is_approved': result.is_approved,
                'entity_name': result.transfer_type_sector,
                'entity_value': result.transfer_quantity
                } for result in results]
            return json_data
        else:
            return None

    @classmethod
    def check_duplicate(cls, transfer_type_id, transfer_sector_id, bt_id):
        return cls.query.filter(cls.transfer_type_id==transfer_type_id, 
                                cls.transfer_sector_id==transfer_sector_id,
                                cls.bt_id==bt_id).first()
    
    def update_db(self):
        db.session.commit()

    def save_to_db(self):
        duplicate_item = self.check_duplicate(self.transfer_type_id, self.transfer_sector_id, self.bt_id)
        if duplicate_item:
            duplicate_item.transfer_quantity = self.transfer_quantity
            duplicate_item.update_db()
        else:
            db.session.add(self)
            db.session.commit()
    
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()