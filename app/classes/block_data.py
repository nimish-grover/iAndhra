from types import SimpleNamespace
from app.models.livestocks import Livestock
from app.models.crops import Crop
from app.models.industries import Industry
from app.models.population import Population
from app.models.waterbody import WaterbodyType
from app.models.lulc import LULC

from flask import url_for
from app.classes.budget_data import BudgetData
from app.models.block_crops import BlockCrop
from app.models.block_ground import BlockGround
from app.models.block_industries import BlockIndustry
from app.models.block_livestocks import BlockLivestock
from app.models.block_lulc import BlockLULC
from app.models.block_pop import BlockPop
from app.models.block_rainfall import BlockRainfall
from app.models.block_surface import BlockWaterbody
from app.models.block_territory import BlockTerritory
from datetime import datetime, timezone

from app.models.block_transfer import BlockWaterTransfer
from app.models.industries import Industry
from app.models.lulc_census import LULCCensus
from app.models.block_progress import BlockProgress
from app.models.block_category import BlockCategory

class BlockData:
    @classmethod
    def get_bt_id(cls,village_id,panchayat_id, block_id, district_id, state_id):
        bt_id = BlockTerritory.get_bt_id(village_id = int(village_id),panchayat_id=int(panchayat_id),block_id=int(block_id), district_id=int(district_id), state_id=int(state_id))
        if bt_id:
            return bt_id
        else:
            block_territory = BlockTerritory(state_id=state_id, district_id=district_id, block_id=block_id,village_id=village_id,panchayat_id=panchayat_id)
            block_territory.save_to_db()
            bt_id = BlockTerritory.get_bt_id(village_id,panchayat_id,block_id, district_id, state_id)
            return bt_id
        
        
    # @classmethod
    # def insert_block_progress(cls,bt_id,category_id,data):
    #     data = 
        
    #     return None
    @classmethod
    def get_category_id(cls,category):
        category_id = BlockCategory.get_category_id(category)
        return category_id
    
    @classmethod
    def get_human_consumption(cls, village_id,panchayat_id,block_id, district_id, user_id, state_id=2):
        bt_id = cls.get_bt_id(village_id=village_id,panchayat_id=panchayat_id,block_id=block_id, district_id=district_id, state_id=state_id)
        return cls.get_or_insert_human(village_id,panchayat_id,block_id, district_id, bt_id, user_id)
    
    # inserted by system
    def get_or_insert_human(village_id,panchayat_id,block_id, district_id, bt_id, user_id):
        human = BlockPop.get_by_bt_id(bt_id)
        category_id = BlockData.get_category_id('human')
        if human:
            for item in human:
                if item['count']:
                    block_progress = BlockProgress(bt_id=item['bt_id'],
                                                    is_approved=item['is_approved'],
                                                    value=item['count'],
                                                    table_id=item['population_id'],
                                                    category_id = category_id)
                    block_progress.save_to_db()
                
            return human
        else:
            human_consumption = BudgetData.get_human_consumption(village_id=village_id,panchayat_id=panchayat_id,block_id=block_id, district_id=district_id)
            if human_consumption:
                for item in human_consumption:
                    block_population = BlockPop(
                                        population_id=item['id'],
                                        count=item['count'],
                                        bt_id=bt_id, 
                                        is_approved=False, 
                                        created_by=user_id)
                    block_population.save_to_db()
                human = BlockPop.get_by_bt_id(bt_id)  
                for item in human:
                    if item['count'] > 0:
                        block_progress = BlockProgress(bt_id=item['bt_id'],
                                                        is_approved=item['is_approved'],
                                                        value=item['count'],
                                                        table_id=item['population_id'],
                                                        category_id = category_id)
                        block_progress.save_to_db()
                return human

    # updated / inserted by user
    def update_human(json_data, user_id):
        for item in json_data: 
            block_population = BlockPop(
                        population_id=item['population_id'],
                        count=item['count'],
                        bt_id=item['bt_id'], 
                        is_approved=True, 
                        created_by=user_id)
            if item['count'] >0:
                block_population.save_to_db()
            else:
                if item['count']==0:
                    if item['table_id']:
                        block_population = None
                        block_population = BlockPop.get_by_id(item['table_id']) 
                        if block_population:
                            block_population.delete_from_db()  
        return True
    
    @classmethod
    def get_dummy_human(cls, village_id,panchayat_id,block_id, district_id, user_id, state_id=2):
        bt_id = cls.get_bt_id(village_id=village_id,panchayat_id=panchayat_id,block_id=block_id, district_id=district_id, state_id=state_id)
        population = Population.get_all_population()
        if population:
            for item in population:
                item['bt_id'] = bt_id
                item['count'] = 0 
                item['table_id'] = 0
            return population
    
    @classmethod
    def get_livestock_consumption(cls, village_id,panchayat_id,block_id, district_id, user_id, state_id=2):
        bt_id = cls.get_bt_id(village_id=village_id,panchayat_id=panchayat_id,block_id=block_id, district_id=district_id, state_id=state_id)
        return cls.get_or_insert_livestock(village_id,panchayat_id,block_id, district_id, bt_id, user_id)
    
    # inserted by system
    def get_or_insert_livestock(village_id,panchayat_id,block_id, district_id, bt_id, user_id):
        livestock = BlockLivestock.get_by_bt_id(bt_id)
        category_id = BlockData.get_category_id('livestock')

        if all(row['table_id'] is None for row in livestock):
            livestock_consumption = BudgetData.get_livestock_consumption(village_id=village_id,panchayat_id=panchayat_id,block_id=block_id, district_id=district_id)
            if livestock_consumption:
                for item in livestock_consumption:
                    block_livestock = BlockLivestock(
                                livestock_id=item['id'],
                                count=item['count'],
                                bt_id=bt_id,
                                is_approved=False, 
                                created_by=user_id)
                    block_livestock.save_to_db()
                livestock = BlockLivestock.get_by_bt_id(bt_id)
                for item in livestock:
                    if item['count'] > 0:
                        block_progress = BlockProgress(bt_id=item['bt_id'],
                                                        is_approved=item['is_approved'],
                                                        value=item['count'],
                                                        table_id=item['livestock_id'],
                                                        category_id = category_id)
                        block_progress.save_to_db()     
                return livestock
        else:
            for item in livestock:
                if item['count']:
                    block_progress = BlockProgress(bt_id=item['bt_id'],
                                                    is_approved=item['is_approved'],
                                                    value=item['count'],
                                                    table_id=item['livestock_id'],
                                                    category_id = category_id)
                    block_progress.save_to_db()
            return livestock
            
    # updated / inserted by user
    def update_livestock(json_data, user_id):
        for item in json_data: 
            block_livestock = BlockLivestock(
                    livestock_id=item['id'],
                    count=item['count'],
                    bt_id=item['bt_id'],
                    is_approved=True, 
                    created_by=user_id)
            if item['count']>0:
                block_livestock.save_to_db()
            else:
                if item['count']==0:
                    if item['table_id']:
                        block_livestock = None
                        block_livestock = BlockLivestock.get_by_id(item['table_id']) 
                        if block_livestock:
                            block_livestock.delete_from_db()  
        return True
    
    @classmethod 
    def get_dummy_livestock(cls,village_id,panchayat_id,block_id,district_id,state_id=2):
        bt_id = cls.get_bt_id(village_id=village_id,panchayat_id=panchayat_id,block_id=block_id, district_id=district_id, state_id=state_id)
        livestocks = Livestock.get_all_livestocks()
        if livestocks:
            for item in livestocks:
                item['bt_id'] = bt_id
                item['count'] = 0 
                item['id'] = item['livestock_id']
                item['table_id'] = 0
            return livestocks

    @classmethod
    def get_crops_consumption(cls,village_id,panchayat_id, block_id, district_id, user_id, state_id=2):
        bt_id = cls.get_bt_id(village_id=village_id,panchayat_id=panchayat_id,block_id=block_id, district_id=district_id, state_id=state_id)
        return cls.get_or_insert_crops(village_id,panchayat_id,block_id, district_id, bt_id, user_id)
    
    def get_or_insert_crops(village_id,panchayat_id,block_id, district_id, bt_id, user_id):
        crops = BlockCrop.get_by_bt_id(bt_id)
        category_id = BlockData.get_category_id('crop')

        if all(row['table_id'] is None for row in crops):
            crops_consumption = BudgetData.get_crops_consumption(village_id=village_id,panchayat_id=panchayat_id,block_id=block_id, district_id=district_id)
            if crops_consumption:
                for item in crops_consumption:
                    block_crops = BlockCrop(
                                crop_id=item['id'],
                                area=item['count'],
                                bt_id=bt_id,
                                is_approved=False, 
                                created_by=user_id)
                    block_crops.save_to_db()
                crops = BlockCrop.get_by_bt_id(bt_id)     
                for item in crops:
                    if item['crop_area']:
                        block_progress = BlockProgress(bt_id=item['bt_id'],
                                                        is_approved=item['is_approved'],
                                                        value=item['crop_area'],
                                                        table_id=item['crop_id'],
                                                        category_id = category_id)
                        block_progress.save_to_db()
                return crops
        else:
            for item in crops:
                if item['crop_area']:
                    block_progress = BlockProgress(bt_id=item['bt_id'],
                                                    is_approved=item['is_approved'],
                                                    value=item['crop_area'],
                                                    table_id=item['crop_id'],
                                                    category_id = category_id)
                    block_progress.save_to_db()
            return crops
    
    def update_crops(json_data, user_id):
        for item in json_data: 
            block_crops = BlockCrop(
                    crop_id=item['crop_id'],
                    area=item['crop_area'],
                    bt_id=item['bt_id'],
                    is_approved=True, 
                    created_by=user_id)
            if item['crop_area']>0:
                block_crops.save_to_db()
            else:
                if item['crop_area']==0:
                    if item['table_id']:
                        block_crops = None
                        block_crops = BlockCrop.get_by_id(item['table_id']) 
                        if block_crops:
                            block_crops.delete_from_db()  
        return True

    @classmethod
    def get_dummy_crops(cls,village_id,panchayat_id,block_id,district_id,state_id=2):
        bt_id = BlockTerritory.get_bt_id(village_id,panchayat_id,block_id, district_id, state_id)
        crops = Crop.get_all_crops()
        if crops:
            for item in crops:
                item['id'] = item['crop_id']
                item['table_id'] = 0
                item['crop_area'] = 0
                item['bt_id'] = bt_id
            return crops
    
    @classmethod
    def get_block_industries(cls, village_id,panchayat_id,block_id, district_id, user_id, state_id=2):
        bt_id = BlockTerritory.get_bt_id(village_id,panchayat_id,block_id, district_id, state_id)
        return cls.get_industries(village_id,panchayat_id,block_id, district_id, bt_id, user_id)

    def get_industries(village_id,panchayat_id,block_id, district_id, bt_id, user_id):
        industries = BlockIndustry.get_by_bt_id(bt_id=bt_id)
        # results =[{'id': item.id, 'category':item.industry_sector } for item in industries]
        category_id = BlockData.get_category_id('industry')

        for item in industries:
            if item['table_id']:
                block_progress = BlockProgress(bt_id=item['bt_id'],
                                                is_approved=item['is_approved'],
                                                value=item['allocation'],
                                                table_id=item['industry_id'],
                                                category_id = category_id)
                block_progress.save_to_db()
            
        return industries
    
    def update_industries(json_data, user_id):
            bt_id = 0 
            category_id = BlockData.get_category_id('industry')
            for item in json_data: 
                bt_id = item['bt_id']
                block_industries = BlockIndustry(
                        industry_id=item['industry_id'],
                        allocation=item['allocation'],
                        unit = item['unit'],
                        count = item['count'],
                        bt_id=item['bt_id'],
                        is_approved=True, 
                        created_by=user_id)
                if item['allocation']>0:
                    block_industries.save_to_db()
                else:
                    if item['allocation']==0:
                        if item['table_id']:
                            block_industries = None
                            block_industries = BlockIndustry.get_by_id(item['table_id']) 
                            if block_industries:
                                block_industries.delete_from_db()  
                                
            # if there is no entry (all zeros) then enter a single row with zero                        
            filtered_json_data = [item for item in json_data if item['count'] > 0]
            if len(filtered_json_data) == 0:
                block_industries = BlockIndustry(
                        industry_id=1,
                        allocation=0,
                        unit = "HaM",
                        count = 0,
                        bt_id=bt_id,
                        is_approved=True, 
                        created_by=1)
                block_industries.save_to_db()
                block_progress = BlockProgress(bt_id=bt_id,
                                                is_approved=True,
                                                value=0,
                                                table_id=1,
                                                category_id = category_id)
                block_progress.save_to_db()
            return True

    @classmethod
    def get_surface_supply(cls, village_id,panchayat_id,block_id, district_id, user_id, state_id=2):
        bt_id = cls.get_bt_id(village_id=village_id,panchayat_id=panchayat_id,block_id=block_id, district_id=district_id, state_id=state_id)
        return cls.get_or_insert_surface_supply(village_id,panchayat_id,block_id, district_id, bt_id, user_id)
    
    def get_or_insert_surface_supply(village_id,panchayat_id,block_id, district_id, bt_id, user_id):
        waterbodies = BlockWaterbody.get_by_bt_id(bt_id)
        category_id = BlockCategory.get_category_id('surface')
        if all(row['table_id'] is None for row in waterbodies):            
            surface_supply = BudgetData.get_surface_supply(village_id=village_id,panchayat_id=panchayat_id,block_id=block_id, district_id=district_id)
            if surface_supply:
                for item in surface_supply:
                    block_surface = BlockWaterbody(
                        wb_type_id = item['id'],
                        count = item['count'],
                        storage=item['value'],
                        bt_id=bt_id,
                        is_approved=False,
                        created_by=user_id
                    )
                    block_surface.save_to_db()
                waterbodies = BlockWaterbody.get_by_bt_id(bt_id)  
                for item in waterbodies:
                    if item['count']:
                        block_progress = BlockProgress(bt_id=item['bt_id'],
                                                        is_approved=item['is_approved'],
                                                        value=item['storage'],
                                                        table_id=item['wb_type_id'],
                                                        category_id = category_id)
                        block_progress.save_to_db()
                return waterbodies
        else:
            for item in waterbodies:
                if item['count']:
                    block_progress = BlockProgress(bt_id=item['bt_id'],
                                                    is_approved=item['is_approved'],
                                                    value=item['storage'],
                                                    table_id=item['wb_type_id'],
                                                    category_id = category_id)
                    block_progress.save_to_db()
            return waterbodies
    
    def update_surface(json_data, user_id):
        for item in json_data: 
            block_surface = BlockWaterbody(
                    wb_type_id=item['wb_type_id'],
                    count=item['count'],
                    storage=item['storage'],
                    bt_id=item['bt_id'],
                    is_approved=True, 
                    created_by=user_id)
            if item['storage'] > 0:
                block_surface.save_to_db()
            else:
                if item['storage']==0:
                    if item['table_id']:
                        block_surface = None
                        block_surface = BlockWaterbody.get_by_id(item['table_id']) 
                        if block_surface:
                            block_surface.delete_from_db()  
        return True
    
    @classmethod
    def get_dummy_surface(cls,village_id,panchayat_id,block_id, district_id, state_id=2):
        bt_id = cls.get_bt_id(village_id=village_id,panchayat_id=panchayat_id,block_id=block_id, district_id=district_id, state_id=state_id)
        surface = WaterbodyType.get_all_waterbodies()
        if surface:
            for item in surface:
                item['count'] = 0
                item['storage'] = 0
                item['bt_id'] = bt_id
                item['table_id'] = 0
            return surface
        
        
    @classmethod
    def get_groundwater_supply(cls, village_id,panchayat_id,block_id, district_id, user_id, state_id=2):
        bt_id = cls.get_bt_id(village_id=village_id,panchayat_id=panchayat_id,block_id=block_id, district_id=district_id, state_id=state_id)
        return cls.get_or_insert_groundwater_supply(village_id,panchayat_id,block_id, district_id, bt_id, user_id)
    
    def get_or_insert_groundwater_supply(village_id,panchayat_id,block_id, district_id, bt_id, user_id):
        groundwater_supply = BlockGround.get_by_bt_id(bt_id)
        category_id = BlockCategory.get_category_id('groundwater')
        if groundwater_supply:
            for item in groundwater_supply:
                if item['extraction']:
                    block_progress = BlockProgress(bt_id=item['bt_id'],
                                                    is_approved=item['is_approved'],
                                                    value=item['extraction'],
                                                    table_id=0,
                                                    category_id = category_id)
                    block_progress.save_to_db()
            return groundwater_supply
        else: 
            groundwater_data = BudgetData.get_ground_supply(village_id,panchayat_id,block_id, district_id)
            for item in groundwater_data:
                item = SimpleNamespace(**item)
                if item.name.lower() == 'extraction':
                    block_ground = BlockGround(extraction=item.value, 
                                            bt_id=bt_id, 
                                            is_approved=False, 
                                            created_by=user_id)
                    block_ground.save_to_db()
            groundwater_supply = BlockGround.get_by_bt_id(bt_id)
            for item in groundwater_supply:
                if item['extraction']:
                    block_progress = BlockProgress(bt_id=item['bt_id'],
                                                    is_approved=item['is_approved'],
                                                    value=item['extraction'],
                                                    table_id=0,
                                                    category_id = category_id)
                    block_progress.save_to_db()
            return groundwater_supply
        
    def update_ground(json_data, user_id):
        for item in json_data: 
            if 'extraction' in item:
                id = item['id']
                block_ground = BlockGround.get_by_id(id)
                block_ground.extraction = item['extraction']
                block_ground.created_by = user_id
                block_ground.is_approved = True
                block_ground.update_db()
        return True
    
    @classmethod
    def get_dummy_groundwater(cls, village_id,panchayat_id,block_id, district_id, state_id=2):
        bt_id = cls.get_bt_id(village_id=village_id,panchayat_id=panchayat_id,block_id=block_id, district_id=district_id, state_id=state_id)
        ground_supply = [{'extraction':0,'bt_id':bt_id,'table_id':0},]
        return ground_supply
    
    @classmethod
    def get_rainfall_data(cls,village_id,panchayat_id,block_id, district_id, user_id, state_id=2):
        bt_id = BlockTerritory.get_bt_id(village_id,panchayat_id,block_id, district_id, state_id)
        return cls.get_or_insert_rainfall_data(village_id,panchayat_id,block_id, district_id, bt_id, user_id)
    
    def get_or_insert_rainfall_data(village_id,panchayat_id,block_id, district_id, bt_id, user_id):
        rainfall = BlockRainfall.get_by_bt_id(bt_id)
        category_id = BlockCategory.get_category_id('rainfall')
        if not rainfall:            
            rainfall_supply = BudgetData.get_rainfall(village_id,panchayat_id,block_id, district_id)
            if rainfall_supply:
                for item in rainfall_supply:
                    block_rainfall = BlockRainfall(normal=item['normal'],
                                                    actual=item['actual'],
                                                    month_year=item['date'],
                                                    bt_id=bt_id,
                                                    is_approved=False,
                                                    created_by=user_id)
                    block_rainfall.save_to_db()
                rainfall = BlockRainfall.get_by_bt_id(bt_id) 
                if rainfall:
                    for idx,item in enumerate(rainfall):
                        if item['normal']:
                            block_progress = BlockProgress(bt_id=item['bt_id'],
                                                            is_approved=item['is_approved'],
                                                            value=item['normal'],
                                                            table_id=idx+1,
                                                            category_id = category_id)
                            block_progress.save_to_db()
                    return rainfall
                else:
                    return None
        else:
            for idx,item in enumerate(rainfall):
                if item['normal']:
                    block_progress = BlockProgress(bt_id=item['bt_id'],
                                                    is_approved=item['is_approved'],
                                                    value=item['normal'],
                                                    table_id=idx+1,
                                                    category_id = category_id)
                    block_progress.save_to_db()
            return rainfall
                
    def update_rainfall(json_data, user_id):
        for item in json_data: 
            block_rainfall = BlockRainfall(
                    normal = item['normal'],
                    actual = item['actual'],
                    bt_id = item['bt_id'],
                    month_year=datetime.strptime(item['month_year'], "%b-%y").replace(day=1),
                    is_approved = True,
                    created_by=user_id)
            block_rainfall.save_to_db()
        return True
    
        
    
    @classmethod
    def get_lulc_supply(cls,village_id,panchayat_id, block_id, district_id, user_id, state_id=2):
        bt_id = BlockTerritory.get_bt_id(village_id,panchayat_id,block_id, district_id, state_id)
        return cls.get_or_insert_lulc(village_id,panchayat_id,block_id, district_id, bt_id, user_id)

    def get_or_insert_lulc(village_id,panchayat_id,block_id, district_id, bt_id, user_id):
        lulc = BlockLULC.get_by_bt_id(bt_id)
        category_id = BlockCategory.get_category_id('lulc')
        if all(row['table_id'] is None for row in lulc):
            lulc_supply = LULCCensus.get_lulc(village_id=village_id,panchayat_id=panchayat_id,block_id=block_id, district_id=district_id)
            if lulc_supply:
                for item in lulc_supply:
                    if item['lulc_area']>0:
                        block_lulc = BlockLULC(
                            lulc_id=item['lulc_id'],
                            area=item['lulc_area'],
                            bt_id=bt_id,
                            is_approved=False,
                            created_by=user_id)
                        block_lulc.save_to_db()
                lulc = BlockLULC.get_by_bt_id(bt_id)     
                for item in lulc:
                    if item['area']:
                        block_progress = BlockProgress(bt_id=item['bt_id'],
                                                        is_approved=item['is_approved'],
                                                        value=item['area'],
                                                        table_id=item['lulc_id'],
                                                        category_id = category_id)
                        block_progress.save_to_db()
                return lulc
        else:
            for item in lulc:
                if item['area']:
                    block_progress = BlockProgress(bt_id=item['bt_id'],
                                                    is_approved=item['is_approved'],
                                                    value=item['area'],
                                                    table_id=item['lulc_id'],
                                                    category_id = category_id)
                    block_progress.save_to_db()
            return lulc
            
    def update_lulc(json_data, user_id):
        for item in json_data: 
            block_lulc = BlockLULC(
                    lulc_id=item['lulc_id'],
                    area=item['area'],
                    bt_id=item['bt_id'],
                    is_approved=True, 
                    created_by=user_id)
            if item['area'] > 0:
                block_lulc.save_to_db()
            else:
                if item['area']==0:
                    if item['table_id']:
                        block_lulc = None
                        block_lulc = BlockLULC.get_by_id(item['table_id']) 
                        if block_lulc:
                            block_lulc.delete_from_db()  
        return True
    
    @classmethod
    def get_dummy_lulc(cls,village_id,panchayat_id,block_id,district_id,state_id=2):
        bt_id = BlockTerritory.get_bt_id(village_id,panchayat_id,block_id, district_id, state_id)
        lulc = LULC.get_all_lulc()
        if lulc:
            for item in lulc:
                item['bt_id'] = bt_id
                item['area'] = 0
                item['table_id'] = 0
            return lulc

    
    @classmethod
    def get_water_transfer(cls, village_id,panchayat_id,block_id, district_id, user_id, state_id=2):
        bt_id = BlockTerritory.get_bt_id(village_id,panchayat_id,block_id, district_id, state_id)
        return cls.get_or_insert_water_transfer(village_id,panchayat_id,block_id, district_id, bt_id, user_id)
    
    def get_or_insert_water_transfer(village_id,panchayat_id,block_id, district_id, bt_id, user_id):
        water_transfer = BlockWaterTransfer.get_by_bt_id(bt_id)
        category_id = BlockData.get_category_id('transfer')

        for item in water_transfer:
            if item['table_id']:
                block_progress = BlockProgress(bt_id=item['bt_id'],
                                                is_approved=item['is_approved'],
                                                value=item['quantity'],
                                                table_id=item['type_id'],
                                                category_id = category_id)
                block_progress.save_to_db()
        return water_transfer
    
    def update_water_transfer(json_data, user_id):
        category_id = BlockCategory.get_category_id('transfer')
        for item in json_data: 
            block_water_transfer = BlockWaterTransfer(
                        transfer_quantity=item['quantity'],
                        transfer_type_id=item['type_id'],
                        transfer_sector_id=item['sector_id'],
                        bt_id=item['bt_id'],
                        is_approved=True,
                        created_by=user_id)
            if item['quantity'] > 0:
                    block_water_transfer.save_to_db()
            else:
                if item['quantity']==0:
                    if item['table_id']:
                        block_water_transfer = None
                        block_water_transfer = BlockWaterTransfer.get_by_id(item['table_id'])
                        if block_water_transfer:
                            block_water_transfer.delete_from_db()     
        filtered_json_data = [item for item in json_data if item['count'] > 0]
        if len(filtered_json_data) == 0:
            block_water_transfer = BlockWaterTransfer(
                        transfer_quantity=0,
                        transfer_type_id=item['type_id'],
                        transfer_sector_id=item['sector_id'],
                        bt_id=item['bt_id'],
                        is_approved=True,
                        created_by=user_id)
            block_water_transfer.save_to_db()
            block_progress = BlockProgress(bt_id=item['bt_id'],
                                                is_approved=True,
                                                value=0,
                                                table_id=item['type_id'],
                                                category_id = category_id)
            block_progress.save_to_db()
        return True
    
    @classmethod
    def get_progress_status(cls, village_id,panchayat_id,block_id, district_id, state_id=2):
        bt_id = cls.get_bt_id(village_id,panchayat_id,block_id, district_id, state_id)
        status = BlockTerritory.get_status_by_bt_id(bt_id)
        query_result = status[0]  # Assuming only one result from the query
        categories = ['Human', 'Livestocks', 'Crops',  'Industry', 'Surface', 'Groundwater', 'LULC', 'Rainfall', 'Water Transfer']
        category_urls = ['human', 'livestocks', 'crops', 'industries', 'surface', 'ground', 'lulc', 'rainfall', 'transfer']

        progress_status = [
            {
                'id': idx + 1,
                'category': category,
                'status': bool(query_result[idx]),
                'url': url_for(f'desktop.{category_urls[idx]}')
            }
            for idx, category in enumerate(categories)
        ]
        return progress_status
    