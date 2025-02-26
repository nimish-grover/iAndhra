from sqlalchemy import Integer, case, cast, func
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
    
    def transform_data_villages(data):
        villages = []
        
        for idx,village_data in enumerate(data):
            if idx == 0 or village_data['village_id'] not in villages:
                pass
    
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
        
    @classmethod
    def get_panchayat_progress(cls):
        query = (
            db.session.query(
                District.short_name,
                District.district_name,
                Block.block_name,
                Panchayat.panchayat_name,
                func.count(func.distinct(Village.id)).label("total_villages"),
                func.count(
                    func.distinct(
                        case(
                            (BlockProgress.is_approved == True, func.concat(BlockProgress.category_id, '-', BlockProgress.bt_id))
                        )
                    )
                ).label("completed_count"),
                func.round(
                    (
                        func.count(
                            func.distinct(
                                case(
                                    (BlockProgress.is_approved == True, func.concat(BlockProgress.category_id, '-', BlockProgress.bt_id))
                                )
                            )
                        ).cast(db.Numeric) / (9 * func.count(func.distinct(Village.id)))
                    ) * 100, 2
                ).label("completed_percentage"),
            )
            .join(Block, Block.district_lgd_code == District.lgd_code)
            .join(Panchayat, Panchayat.block_lgd_code == Block.lgd_code)
            .join(Village, Village.panchayat_lgd_code == Panchayat.lgd_code)
            .outerjoin(
                BlockTerritory,
                (BlockTerritory.district_id == District.id) &
                (BlockTerritory.panchayat_id == Panchayat.id) &
                (BlockTerritory.block_id == Block.id)
            )
            .outerjoin(BlockProgress, BlockProgress.bt_id == BlockTerritory.id)
            .group_by(
                District.short_name,
                District.district_name,
                Block.block_name,
                Panchayat.panchayat_name
            )
            .having(
                func.count(
                    func.distinct(
                        case(
                            (BlockProgress.is_approved == True, func.concat(BlockProgress.category_id, '-', BlockProgress.bt_id))
                        )
                    )
                ) > 0
            )
            .order_by(
                "completed_percentage",
                "completed_count",
                District.district_name,
                Panchayat.panchayat_name
            )
        )
        
        results = query.all()
        progress_data = [{'district_short_name':item[0],
                        'district_name':item[1],
                        'block_name':item[2],
                        'panchayat_name':item[3],
                        'total_villages':item[4],
                        'completed_count':item[5],
                        'completed_percentage':int(item[6])} for item in results]
        return progress_data
    
        """
        SELECT
        d.short_name,
        d.district_name,
        b.block_name,
        p.panchayat_name,
        COUNT(DISTINCT v.id) AS total_villages,
        COUNT(DISTINCT CASE WHEN bp.is_approved = true THEN CONCAT(bp.category_id, '-', bp.bt_id) END) AS completed_count,
        ROUND(
            (COUNT(DISTINCT CASE WHEN bp.is_approved = true THEN CONCAT(bp.category_id, '-', bp.bt_id) END)::decimal / (9 * COUNT(DISTINCT v.id))) * 100,
            2
        ) AS completed_percentage
    FROM
        districts d
        JOIN blocks b ON b.district_lgd_code = d.lgd_code
        JOIN panchayats p ON p.block_lgd_code = b.lgd_code
        JOIN villages v ON v.panchayat_lgd_code = p.lgd_code
        LEFT JOIN block_territory bt ON bt.district_id = d.id AND bt.panchayat_id = p.id AND bt.block_id = b.id
        LEFT JOIN block_progress bp ON bp.bt_id = bt.id
    GROUP BY
        d.short_name,
        d.district_name,
        b.block_name,
        p.panchayat_name
    HAVING
        COUNT(DISTINCT CASE WHEN bp.is_approved = true THEN CONCAT(bp.category_id, '-', bp.bt_id) END) > 0
    ORDER BY
        completed_percentage,
        completed_count,
        d.district_name,
        p.panchayat_name;
        """
    @classmethod
    def get_district_progress(cls):
        query = (
            db.session.query(
                District.short_name,
                District.district_name,
                func.count(func.distinct(Village.id)).label("total_villages"),
                func.count(
                    func.distinct(
                        case(
                            (BlockProgress.is_approved == True, BlockProgress.category_id)
                        )
                    )
                ).label("completed_count"),
                func.round(
                    (
                        func.count(
                            func.distinct(
                                case(
                                    (BlockProgress.is_approved == True, BlockProgress.category_id)
                                )
                            )
                        ).cast(db.Numeric) / (9 * func.count(func.distinct(Village.id)))
                    ) * 100, 2
                ).label("completed_percentage"),
            )
            .join(Village, Village.district_lgd_code == District.lgd_code)
            .outerjoin(BlockTerritory, BlockTerritory.district_id == District.id)
            .outerjoin(BlockProgress, BlockProgress.bt_id == BlockTerritory.id)
            .group_by(District.district_name, District.short_name)
            .order_by(District.district_name)
        )
        results = query.all()
        progress_data = [{'district_short_name':item[0],
                        'district_name':item[1],
                        'total_villages':item[2],
                        'completed_count':item[3],
                        'completed_percentage':item[4]} for item in results]
        return progress_data
        """
        SELECT
            d.district_name,
            COUNT(DISTINCT v.id) AS total_villages,
            COUNT(DISTINCT CASE WHEN bp.is_approved = true THEN bp.category_id END) AS completed_count,
            ROUND(
                (COUNT(DISTINCT CASE WHEN bp.is_approved = true THEN bp.category_id END)::decimal / 
                (9 * COUNT(DISTINCT v.id))) * 100,
                2
            ) AS completed_percentage
        FROM
            districts d
            JOIN villages v ON v.district_lgd_code = d.lgd_code
            LEFT JOIN block_territory bt ON bt.district_id = d.id
            LEFT JOIN block_progress bp ON bp.bt_id = bt.id
        GROUP BY
            d.district_name
        ORDER BY
            d.district_name;
        """
    @classmethod
    def get_village_progress(cls):
        query = (
                db.session.query(
                    District.short_name,
                    District.district_name,
                    Block.block_name,
                    Panchayat.panchayat_name,
                    Village.village_name,
                    Village.id.label("village_id"),
                    Block.id.label("block_id"),
                    Panchayat.id.label("panchayat_id"),
                    District.id.label("district_id"),
                    func.count(
                        func.distinct(
                            case(
                                (BlockProgress.is_approved == True, func.concat(BlockProgress.category_id, '-', BlockProgress.bt_id))
                            )
                        )
                    ).label("completed_count"),
                    func.round(
                        (
                            func.count(
                                func.distinct(
                                    case(
                                        (BlockProgress.is_approved == True, func.concat(BlockProgress.category_id, '-', BlockProgress.bt_id))
                                    )
                                )
                            ).cast(db.Numeric) / 9
                        ) * 100, 2
                    ).label("completed_percentage"),
                )
                .join(Block, Block.district_lgd_code == District.lgd_code)
                .join(Panchayat, Panchayat.block_lgd_code == Block.lgd_code)
                .join(Village, Village.panchayat_lgd_code == Panchayat.lgd_code)
                .outerjoin(
                    BlockTerritory,
                    (BlockTerritory.district_id == District.id) &
                    (BlockTerritory.panchayat_id == Panchayat.id) &
                    (BlockTerritory.block_id == Block.id) &
                    (BlockTerritory.village_id == Village.id)
                )
                .outerjoin(BlockProgress, BlockProgress.bt_id == BlockTerritory.id)
                .group_by(
                    District.short_name,
                    District.district_name,
                    Block.block_name,
                    Panchayat.panchayat_name,
                    Village.village_name,
                    Village.id,
                    Block.id,
                    Panchayat.id,
                    District.id
                )
                .having(
                    func.count(
                        func.distinct(
                            case(
                                (BlockProgress.is_approved == True, func.concat(BlockProgress.category_id, '-', BlockProgress.bt_id))
                            )
                        )
                    ) > 0
                )
                .order_by(
                    "completed_count",
                    District.district_name,
                    Panchayat.panchayat_name
                )
            )
        results = query.all()
        progress_data = [{'district_short_name':item[0],
                        'district_name':item[1],
                        'block_name':item[2],
                        'panchayat_name':item[3],
                        'village_name':item[4],
                        'village_id':item[5],
                        'block_id':item[6],
                        'panchayat_id':item[7],
                        'district_id':item[8],
                        'completed_count':item[9],
                        'completed_percentage':item[10]} for item in results]
        return progress_data        
        """
    SELECT
        d.short_name,
        d.district_name,
        b.block_name,
        p.panchayat_name,
        v.village_name,
        v.id as village_id,
        b.id as block_id,
        p.id as panchayat_id,
        d.id as district_id,
        COUNT(DISTINCT CASE WHEN bp.is_approved = true THEN CONCAT(bp.category_id, '-', bp.bt_id) END) AS completed_count,
        ROUND(
            (COUNT(DISTINCT CASE WHEN bp.is_approved = true THEN CONCAT(bp.category_id, '-', bp.bt_id) END)::decimal /9)*100,
            2
        ) AS completed_percentage
    FROM
        districts d
        JOIN blocks b ON b.district_lgd_code = d.lgd_code
        JOIN panchayats p ON p.block_lgd_code = b.lgd_code
        JOIN villages v ON v.panchayat_lgd_code = p.lgd_code
        LEFT JOIN block_territory bt ON bt.district_id = d.id AND bt.panchayat_id = p.id AND bt.block_id = b.id and bt.village_id = v.id
        LEFT JOIN block_progress bp ON bp.bt_id = bt.id
    GROUP BY
        d.short_name,
        d.district_name,
        b.block_name,
        p.panchayat_name,
        v.village_name,
        v.id,
        b.id,
        p.id,
        d.id
    HAVING
        COUNT(DISTINCT CASE WHEN bp.is_approved = true THEN CONCAT(bp.category_id, '-', bp.bt_id) END) > 0
    ORDER BY
        completed_count,
        d.district_name,
        p.panchayat_name;
        """
        
