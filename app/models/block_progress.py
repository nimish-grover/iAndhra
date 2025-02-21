from sqlalchemy import Integer, cast, func
from app.db import db
from datetime import datetime
from zoneinfo import ZoneInfo
from app.models.districts import District
from app.models.blocks import Block
from app.models.panchayats import Panchayat
from app.models.villages import Village
from app.models.block_territory import BlockTerritory
from app.models.block_category import BlockCategory

class BlockProgress(db.Model):
    def get_current_time():
        return datetime.now(ZoneInfo('Asia/Kolkata'))
    __tablename__ = 'block_progress'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    bt_id = db.Column(db.Integer, db.ForeignKey('block_territory.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('block_category.id'), nullable=False)
    table_id = db.Column(db.Integer, nullable=False)
    value = db.Column(db.Float, nullable=False)
    is_approved = db.Column(db.Boolean, nullable=False, default=False)
    created_on = db.Column(db.DateTime, default=get_current_time)

    # Relationships (if needed)
    block_territory = db.relationship('BlockTerritory', backref=db.backref('block_progress', lazy='dynamic'))
    block_category = db.relationship('BlockCategory', backref=db.backref('block_progress', lazy='dynamic'))
    
    def __init__(self, bt_id, is_approved, category_id, value,table_id):

        self.bt_id = bt_id
        self.is_approved = is_approved
        self.category_id = category_id
        self.value = value
        self.table_id = table_id
        
    def json(self):
        """
        Returns a JSON serializable dictionary representation of the Village instance.
        """
        return {
            "id": self.id,
            "bt_id": self.bt_id,
            "is_approved": self.is_approved,
            "created_on": self.created_on,
            "category_id": self.category_id,
            "value": self.value,
            "table_id": self.table_id
        }
        
    @classmethod
    def check_duplicate(cls, category_id,table_id, bt_id):
        return cls.query.filter(cls.table_id==table_id,cls.category_id==category_id,cls.bt_id==bt_id).first()
    
    @classmethod
    def get_progress_check(cls,bt_id,category_id):
        query = db.session.query(cls.id).filter(cls.bt_id == bt_id, cls.category_id==category_id).all()
        if query:
            return True
        
    def transform_data_districts(data):
        output = []
        colors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4']
        color_index = 0

        for district in data:
            district_id = district['district_id']
            district_data = district['data']

            # Calculate percentage/completed (assume 100% completion if all `is_approved` are 1)
            completed = sum(1 for entry in district_data if entry['is_approved'] == 1)
            percentage = completed * 100 // len(district_data)

            # Take the first entry as representative for static fields
            first_entry = district_data[0]
            temp_dict={}
            temp_dict['district_id'] = first_entry['district_id']
            temp_dict['district_name']=first_entry['district_name']
            temp_dict['district_short_name']=first_entry['district_short_name']
            temp_dict['category_id'] = first_entry['category_id']
            temp_dict['completed']= percentage
            temp_dict['percentage'] = percentage
            temp_dict['bt_id'] = first_entry['bt_id']
            temp_dict['color']= colors[color_index % len(colors)]
            for district in district_data:
                category_id = district['category_id']
                if category_id:
                    category=BlockCategory.get_category_name(category_id)
                    temp_dict[category] = district['is_approved']
            output.append(temp_dict)
            color_index += 1
            
        sorted_dict = sorted(output, key=lambda x: x["completed"])
        for idx, item in enumerate(sorted_dict):
            item['id'] = idx + 1
        return sorted_dict
    
    def transform_data_villages(data):
        output = []
        colors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4']
        color_index = 0

        for panchayat in data:
            panchayat_id = panchayat['panchayat_id']
            panchayat_data = panchayat['data']

            # Calculate percentage/completed (assume 100% completion if all `is_approved` are 1)
            completed = sum(1 for entry in panchayat_data if entry['is_approved'] == 1)
            percentage = completed * 100 // len(panchayat_data)

            # Take the first entry as representative for static fields
            first_entry = panchayat_data[0]
            temp_dict={}
            temp_dict['block_id'] = first_entry['block_id']
            temp_dict['district_id'] = first_entry['district_id']
            temp_dict['panchayat_id'] = first_entry['panchayat_id']
            temp_dict['district_name']=first_entry['district_name']
            temp_dict['district_short_name']=first_entry['district_short_name']
            temp_dict['block_name']= first_entry['block_name']
            temp_dict['panchayat_name'] = first_entry['panchayat_name']
            temp_dict['category_id'] = first_entry['category_id']
            temp_dict['completed']= percentage
            temp_dict['percentage'] = percentage
            temp_dict['bt_id'] = first_entry['bt_id']
            temp_dict['color']= colors[color_index % len(colors)]
            for panchayat in panchayat_data:
                category_id = panchayat['category_id']
                if category_id:
                    category=BlockCategory.get_category_name(category_id)
                    temp_dict[category] = panchayat['is_approved']
            output.append(temp_dict)
            color_index += 1
            
        sorted_dict = sorted(output, key=lambda x: x["completed"])
        for idx, item in enumerate(sorted_dict):
            item['id'] = idx + 1
        return sorted_dict

    @classmethod
    def get_all_villages_status(cls):
        query = (
                db.session.query(
                    District.district_name.label("district_name"),
                    District.short_name.label("district_short_name"),
                    District.id.label("district_id"),
                    Block.block_name.label("block_name"),
                    Block.id.label("block_id"),
                    Panchayat.id.label("panchayat_id"),
                    Panchayat.panchayat_name.label("panchayat_name"),
                    func.coalesce(BlockProgress.category_id, 0).label("category_id"),
                    func.coalesce(BlockProgress.bt_id, 0).label("bt_id"),
                    func.coalesce(func.min(cast(BlockProgress.is_approved, Integer)), 0).label("is_approved"),
                )
                .outerjoin(BlockTerritory, BlockTerritory.panchayat_id == Panchayat.id)
                .outerjoin(BlockProgress, BlockProgress.bt_id == BlockTerritory.id)
                .outerjoin(Block, Panchayat.block_lgd_code == Block.lgd_code)
                .outerjoin(District, Block.district_lgd_code == District.lgd_code)
                .group_by(
                    BlockProgress.category_id,
                    District.district_name,
                    District.short_name,
                    District.id,
                    Block.block_name,
                    Block.id,
                    Panchayat.id,
                    Panchayat.panchayat_name,
                    BlockProgress.bt_id,
                )
                .order_by(BlockProgress.bt_id, BlockProgress.category_id)
            )
        
        results = query.all()
        grouped_data = {}
        for row in results:
            panchayat_id = str(row[6])  # Convert block_id to string for consistency
            # Create a dictionary for each row
            row_dict = {
                "district_name": row[0],
                "district_short_name": row[1],
                "district_id": row[2],
                "block_name": row[3],
                "block_id": row[4],
                "panchayat_id": row[5],
                "panchayat_name": row[6],
                "category_id": row[7],
                "bt_id": row[8],
                "is_approved": row[9],
            }
            # Check if the block_id already exists in grouped_data
            if panchayat_id not in grouped_data:
                grouped_data[str(panchayat_id)] = []  # Initialize with an empty list
            grouped_data[str(panchayat_id)].append(row_dict)  # Append the row to the group

        # Convert grouped data to the desired format
        result = [{"panchayat_id": panchayat_id, "data": rows} for panchayat_id, rows in grouped_data.items()]
        
        return BlockProgress.transform_data_villages(result)

    @classmethod
    def get_all_districts_status(cls):
        query = (
                db.session.query(
                    District.district_name.label("district_name"),
                    District.short_name.label("district_short_name"),
                    District.id.label("district_id"),
                    func.coalesce(BlockProgress.category_id, 0).label("category_id"),
                    func.coalesce(BlockProgress.bt_id, 0).label("bt_id"),
                    func.coalesce(func.min(cast(BlockProgress.is_approved, Integer)), 0).label("is_approved"),
                )
                .outerjoin(BlockTerritory, BlockTerritory.district_id == District.id)
                .outerjoin(BlockProgress, BlockProgress.bt_id == BlockTerritory.id)
                .group_by(
                    BlockProgress.category_id,
                    District.district_name,
                    District.short_name,
                    District.id,
                    BlockProgress.bt_id,
                )
                .order_by(BlockProgress.bt_id, BlockProgress.category_id)
            )
        
        results = query.all()
        grouped_data = {}
        for row in results:
            district_id = str(row[2])  # Convert block_id to string for consistency
            # Create a dictionary for each row
            row_dict = {
                "district_name": row[0],
                "district_short_name": row[1],
                "district_id": row[2],
                "category_id": row[3],
                "bt_id": row[4],
                "is_approved": row[5],
            }
            # Check if the block_id already exists in grouped_data
            if district_id not in grouped_data:
                grouped_data[str(district_id)] = []  # Initialize with an empty list
            grouped_data[str(district_id)].append(row_dict)  # Append the row to the group

        # Convert grouped data to the desired format
        result = [{"district_id": district_id, "data": rows} for district_id, rows in grouped_data.items()]
        
        return BlockProgress.transform_data_districts(result)

    @classmethod
    def get_status_by_bt_id(cls, bt_id):
        query = (
            db.session.query(
                BlockCategory.id.label("category_id"),
                func.coalesce(BlockProgress.bt_id, 0).label("bt_id"),
                func.coalesce(BlockProgress.is_approved, False).label("is_approved")
            )
            .outerjoin(BlockProgress, 
                       (BlockProgress.category_id == BlockCategory.id) & 
                       (BlockProgress.bt_id == bt_id))  # Applying condition in JOIN
            .distinct(BlockCategory.id, BlockProgress.bt_id, BlockProgress.is_approved)
            .order_by(BlockCategory.id)
        )

        results = query.all()
        return results

    
    def save_to_db(self):
        duplicate_item = self.check_duplicate(self.category_id,self.table_id,self.bt_id)
        if duplicate_item:
            duplicate_item.value = self.value
            duplicate_item.created_on = BlockProgress.get_current_time()
            duplicate_item.is_approved = self.is_approved
            duplicate_item.update_db()
        else:
            db.session.add(self)
        db.session.commit()
        
    def update_db(self):
        db.session.commit()
    
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()