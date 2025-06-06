from itertools import cycle
import random
from app.classes.block_data import BlockData
from app.classes.budget_data import BudgetData
from app.models.block_crops import BlockCrop
from app.models.block_ground import BlockGround
from app.models.block_industries import BlockIndustry
from app.models.block_livestocks import BlockLivestock
from app.models.block_lulc import BlockLULC
from app.models.block_pop import BlockPop
from app.models.block_rainfall import BlockRainfall
from app.models.block_surface import BlockWaterbody
from app.models.lulc_census import LULCCensus
from app.models.strange_table import StrangeTable


class BlockOrCensus:
    
    NUMBER_OF_DAYS = 365 # Number of days in a year 
    DECADAL_GROWTH = 1.25 # Decadal growth @ of 25%
    RURAL_CONSUMPTION = 55 # Human consumption of water in rural areas in Litres
    URBAN_CONSUMPTION = 70 # Human consumption of water in urban areas in Litres
    LITRE_TO_HECTARE = 10000000 # Constant for converting hectare to litres
    WATER_LOSS = 1.15 # add 15% transmission loss to consumption 
    CUM_TO_HAM = 10000 #Constant for converting hectare meter to cubic meter
    # COLORS = ['#5470c6','#91cc75','#fac858','#ee6666','#73c0de','#3ba272','#fc8452','#9a60b4']
    COLORS=['#973EFA','#FA3ECE','#D540FA','#5A3EFA','#FA3E5E','#E592FA','#EB78C7','#B492FF']

    @classmethod
    def get_randomized_colors(cls):
        randomized_colors = cls.COLORS[:]
        random.shuffle(randomized_colors)
        return randomized_colors
    
    @classmethod
    def litre_to_hectare_meters(cls, value):
        return value/cls.LITRE_TO_HECTARE
    
    @classmethod
    def cubic_meter_to_hectare_meters(cls, value):
        return value/cls.CUM_TO_HAM

    @classmethod
    def get_human_data(cls, panchayat_id,block_id, district_id, state_id=2):
        #return block data
        bt_id = BlockData.get_bt_id(panchayat_id=panchayat_id,block_id=block_id, district_id=district_id, state_id=state_id)
        if bt_id:
            human = BlockPop.get_block_population_data(bt_id)
            if human: 
                for item in human:
                    item['entity_consumption'] = round(
                        cls.litre_to_hectare_meters(
                        (int(item['entity_count']) * cls.RURAL_CONSUMPTION 
                        * cls.DECADAL_GROWTH * cls.NUMBER_OF_DAYS * cls.WATER_LOSS)), 2)
                human_consumption = cls.get_entity_consumption(human, cls.COLORS)
                is_approved = (
                        all(row['is_approved'] for row in human if row['is_approved'] is not None) 
                        and any(row['is_approved'] is not None for row in human)
                    )
                if is_approved:
                    return human_consumption, is_approved           
            # else return budget data
        human_consumption = BudgetData.get_human_consumption(panchayat_id,block_id, district_id)
        return human_consumption, False
    
    @classmethod
    def get_livestock_data(cls,panchayat_id, block_id, district_id, state_id=2):
        bt_id = BlockData.get_bt_id(panchayat_id=panchayat_id,block_id=block_id, district_id=district_id, state_id=state_id)
        if bt_id:
            livestocks = BlockLivestock.get_block_livestock_data(bt_id)
            if livestocks:
                for item in livestocks:
                    item['entity_consumption'] = round(cls.litre_to_hectare_meters(
                        float(item['entity_count']) * float(item['coefficient']) 
                        * cls.NUMBER_OF_DAYS),2) 
                is_approved = (
                    all(row['is_approved'] for row in livestocks if row['is_approved'] is not None) 
                    and any(row['is_approved'] is not None for row in livestocks)
                )
                livestock_consumption = cls.get_entity_consumption(livestocks, cls.COLORS)
                if is_approved:
                    return livestock_consumption, is_approved   
        livestock_consumption = BudgetData.get_livestock_consumption(panchayat_id,block_id, district_id)
        return livestock_consumption, False
    
    @classmethod
    def get_crop_data(cls, panchayat_id,block_id, district_id, state_id=2):
        bt_id = BlockData.get_bt_id(panchayat_id=panchayat_id,block_id=block_id, district_id=district_id, state_id=state_id)
        if bt_id:
            crops = BlockCrop.get_block_crop_data(bt_id)
            if crops:
                for item in crops:
                    item['entity_consumption'] = round(
                        float(item['entity_count']) * float(item['coefficient']),2)         
                is_approved = (
                    all(row['is_approved'] for row in crops if row['is_approved'] is not None) 
                    and any(row['is_approved'] is not None for row in crops)
                )
                crop_consumption = cls.get_entity_consumption(crops, cls.COLORS)
                if is_approved:
                    return crop_consumption, is_approved 
        crop_consumption = BudgetData.get_crops_consumption(panchayat_id,block_id, district_id)
        return crop_consumption, False

    @classmethod
    def get_industry_data(cls, panchayat_id,block_id, district_id, state_id=2):
        bt_id = BlockData.get_bt_id(panchayat_id=panchayat_id,block_id=block_id, district_id=district_id, state_id=state_id)
        if bt_id:
            industries = BlockIndustry.get_block_industry_data(bt_id)
            if industries:       
                is_approved = (
                    all(row['is_approved'] for row in industries if row['is_approved'] is not None) 
                    and any(row['is_approved'] is not None for row in industries)
                )
                industry_consumption = cls.get_entity_consumption(industries, cls.COLORS)
                if is_approved:
                    return industry_consumption, is_approved 
        industry_consumption = BlockIndustry.get_block_industry_data()
        return industry_consumption, False
    
    @classmethod
    def get_surface_data(cls,panchayat_id, block_id, district_id, state_id=2):
        bt_id = BlockData.get_bt_id(panchayat_id=panchayat_id,block_id=block_id, district_id=district_id, state_id=state_id)
        if bt_id:
            surface_water = BlockWaterbody.get_block_waterbody_data(bt_id)
            if surface_water:
                is_approved = (
                    all(row['is_approved'] for row in surface_water if row['is_approved'] is not None) 
                    and any(row['is_approved'] is not None for row in surface_water)
                )
                surface_water_supply = cls.get_entity_consumption(surface_water, cls.COLORS)
                if is_approved:
                    return surface_water_supply, is_approved
        surface_water_supply = BudgetData.get_surface_supply(panchayat_id,block_id, district_id)
        return surface_water_supply, False

    @classmethod
    def get_ground_data(cls,panchayat_id, block_id, district_id, state_id=2):
        bt_id = BlockData.get_bt_id(panchayat_id=panchayat_id,block_id=block_id, district_id=district_id, state_id=state_id)
        ground_water_supply = BudgetData.get_ground_supply(panchayat_id,block_id, district_id)
        if bt_id:
            ground_water = BlockGround.get_block_groundwater_data(bt_id)
            if ground_water:
                for item in ground_water_supply:
                    if item['name'] == 'extraction':
                        extraction = ground_water['extraction']
                        item['value'] = extraction
                    elif item['name'].lower()=='extractable':
                        extractable = item['value']
                    elif item['name'].lower()=='stage_of_extraction':
                        if extractable:
                            stage_of_extraction = round((ground_water['extraction']/extractable) * 100, 2)
                            item['value'] = stage_of_extraction
                    elif item['name'].lower() == 'category':
                        category = 'safe'
                        if stage_of_extraction > 70 and stage_of_extraction <= 90:
                            category = 'semi-critical'
                        elif stage_of_extraction > 90 and stage_of_extraction <= 100:
                            category = 'critical'
                        elif stage_of_extraction > 100:
                            category = 'over-exploited'
                        item['value'] = category
                        
                is_approved = ground_water['is_approved']
                if is_approved:
                    return ground_water_supply, is_approved
        # ground_water_supply = BudgetData.get_ground_supply(block_id, district_id)
        ground_water_supply.insert(2,{'name':'Extraction Percentage','value':str(round(ground_water_supply[1]['value']/ground_water_supply[0]['value']*100,2))+' %'})
        return ground_water_supply, False
    
    @classmethod
    def get_runoff_data(cls,panchayat_id, block_id, district_id, state_id=2):  
        bt_id = BlockData.get_bt_id(panchayat_id=panchayat_id,block_id=block_id, district_id=district_id, state_id=state_id)
        rainfall_data = BlockRainfall.get_rainfall_data(bt_id)
        if rainfall_data:
            rainfall_in_mm = float(sum(item['actual'] for item in rainfall_data))
            if rainfall_in_mm > 1500:
                rainfall_in_mm = 1500
            runoff_data = StrangeTable.get_runoff_by_rainfall(rainfall_in_mm)
            if bt_id:
                lulc_data = BlockLULC.get_block_lulc_data(bt_id)
                if lulc_data:
                    is_approved = all(item['is_approved'] for item in lulc_data)
                    runoff_array = []
                    for key,value in runoff_data[0].items():
                        if not key=='rainfall_in_mm':
                            catchment_area = [item['catchment_area'] for item in lulc_data if item['catchment'] == key.lower()][0]
                            runoff_yield = round((value/10) * rainfall_in_mm, 2)
                            catchment_yield = round(catchment_area * runoff_yield, 2)
                            item = {'catchment': key, 
                                    'runoff': value, 
                                    'runoff_yield': runoff_yield, 
                                    'supply': round(cls.cubic_meter_to_hectare_meters(catchment_yield),2)}
                            runoff_array.append(item)
                    bg_colors = cls.COLORS
                    runoff = [{**item, 'background': bg} for item, bg in zip(runoff_array, bg_colors)]
                    if is_approved:
                        return runoff, is_approved
        runoff = BudgetData.get_runoff(panchayat_id,block_id, district_id)
        return runoff, False
    
    @classmethod
    def get_rainfall_data(cls,panchayat_id, block_id, district_id, state_id=2):
        bt_id = BlockData.get_bt_id(panchayat_id=panchayat_id,block_id=block_id, district_id=district_id, state_id=state_id)
        if bt_id:
            rainfall = BlockRainfall.get_rainfall_data(bt_id)
            if rainfall:
                is_approved = (
                    all(row['is_approved'] for row in rainfall if row['is_approved'] is not None) 
                    and any(row['is_approved'] is not None for row in rainfall)
                )
                if is_approved:
                    return rainfall, is_approved
        rainfall_data = BudgetData.get_rainfall(panchayat_id,block_id, district_id)
        return rainfall_data, False
    
    @classmethod
    def get_demand_side_data(cls,panchayat_id, block_id, district_id, state_id=2):
        demand_side = []
        total_human = 0
        total_crop = 0
        total_livestock = 0
        total_industry = 0
        human,is_approved = cls.get_human_data(panchayat_id,block_id, district_id,state_id)
        if human:
            total_human = round(sum([float(item['value']) for item in human]), 2)
        livestocks,is_approved = cls.get_livestock_data(panchayat_id,block_id, district_id,state_id)
        if livestocks:
            total_livestock = round(sum([item['value']for item in livestocks]),2)
        crops,is_approved = cls.get_crop_data(panchayat_id,block_id, district_id,state_id)
        if crops:
            total_crop = round(sum([item['value'] for item in crops]),2)
        industry = BudgetData.get_industry_demand(panchayat_id,block_id, district_id,state_id)
        if industry:
            total_industry = round(sum([float(item['value']) for item in industry]), 2)
        total_demand = total_human + total_livestock + total_crop + total_industry
        demand_side.append({'category': 'Human','value':round((total_human*100)/(total_demand),0),'water_value':total_human})
        demand_side.append({'category': 'Livestock','value':round((total_livestock*100)/(total_demand),0),'water_value':total_livestock})
        demand_side.append({'category': 'Crop','value':round((total_crop*100)/(total_demand),0),'water_value':total_crop})
        demand_side.append({'category': 'Industry','value':round((total_industry*100)/(total_demand),0),'water_value':total_industry}) 
        bg_colors = cls.COLORS
        demand_with_colors = [{**item, 'background': bg} for item, bg in zip(demand_side, bg_colors)]       
        return demand_with_colors

    @classmethod
    def get_supply_side_data(cls,panchayat_id,block_id, district_id, state_id=2):
        supply_side = []
        total_surface = 0
        total_ground = 0
        total_transfer = 0 
        total_runoff = 0
        surface,is_approved = cls.get_surface_data(panchayat_id,block_id, district_id,state_id)
        if surface:
            total_surface = sum([item['value'] for item in surface])
        ground,is_approved = cls.get_ground_data(panchayat_id,block_id, district_id,state_id)
        if ground:
            total_ground = [item['value'] for item in ground if item['name'] == 'extraction'][0]
        transfer = BudgetData.get_water_transfer(panchayat_id,block_id, district_id,state_id)
        runoff ,is_approved = cls.get_runoff_data(panchayat_id,block_id, district_id,state_id)
        if runoff:
            total_runoff = sum([item['supply'] for item in runoff])
        if transfer:
            total_transfer = sum([item['entity_value'] for item in transfer])
        positive_transfer = 0
        if total_transfer > 0: 
            positive_transfer = total_transfer
        total_supply = total_surface + total_ground +total_runoff + total_transfer
        supply_side.append({'category':'Surface', 'value':round((total_surface*100)/(total_supply),0),'water_value':total_surface})
        supply_side.append({'category':'Ground', 'value':round((total_ground*100)/(total_supply),0),'water_value':total_ground})
        supply_side.append({'category':'Runoff', 'value':round((total_runoff*100)/(total_supply),0),'water_value':total_runoff})
        supply_side.append({'category':'Transfer', 'value':round((positive_transfer*100)/(total_supply),0),'water_value':total_transfer})
        bg_colors = cls.COLORS
        supply_with_colors = [{**item, 'background': bg} for item, bg in zip(supply_side, bg_colors)]
        return supply_with_colors
    
    @classmethod
    def get_water_budget_data(cls,panchayat_id, block_id, district_id, state_id=2):
        water_budget = []
        demand_side = cls.get_demand_side_data(panchayat_id,block_id, district_id,state_id)
        total_demand = sum([item['water_value'] for item in demand_side])
        supply_side = cls.get_supply_side_data(panchayat_id,block_id, district_id, state_id)
        total_supply = sum([item['water_value'] for item in supply_side])
        water_budget.append({'category':'Demand', 'value': round((total_demand*100)/(total_demand + total_supply),0),'water_value':total_demand})
        water_budget.append({'category':'Supply', 'value': round((total_supply*100)/(total_demand + total_supply),0),'water_value':total_supply})
        bg_colors = cls.COLORS
        budget_with_colors = [{**item, 'background': bg} for item, bg in zip(water_budget, bg_colors)] 
        return budget_with_colors
    
    @classmethod
    def get_entity_consumption(cls, entity_array, bg_array):
        new_array=[]
        for item in entity_array:
            entity_item =  {'id':0,'category':'', 'count':0.00,'value': 0.00, 'is_approved':False}
            entity_item['category'] = str(item['entity_name'])
            entity_item['count'] = round(item['entity_count'],2)
            entity_item['value'] = round(item['entity_consumption'],2)
            entity_item['id'] = item['entity_id']
            entity_item['is_approved'] = item['is_approved']
            new_array.append(entity_item)
        entity_consumption = [{**item, 'background': bg} for item, bg in zip(new_array, cycle(bg_array))]
        return entity_consumption

    @classmethod
    def get_tga(cls,panchayat_id, block_id, district_id, state_id=2):
        bt_id = BlockData.get_bt_id(panchayat_id=panchayat_id,block_id=block_id, district_id=district_id, state_id=state_id)
        if bt_id:
            lulc_data = BlockLULC.get_block_lulc_data(bt_id)
            if lulc_data:
                is_approved = (
                    all(row['is_approved'] for row in lulc_data if row['is_approved'] is not None) 
                    and any(row['is_approved'] is not None for row in lulc_data)
                )
                if is_approved:
                    return sum(item['catchment_area'] for item in lulc_data)
        
        lulc_data = LULCCensus.get_census_data_lulc(panchayat_id,block_id, district_id)
        return sum(item['catchment_area'] for item in lulc_data)
    
    @classmethod
    def get_secondary_demand(cls,panchayat_id,block_id,district_id,state_id):
        secondary_human = 0
        secondary_livestock = 0
        secondary_crop = 0
        secondary_industry = 0
        human = BudgetData.get_human_consumption(panchayat_id,block_id,district_id)
        if human:
            secondary_human = round(sum([float(item['value']) for item in human]), 2)
        livestock = BudgetData.get_livestock_consumption(panchayat_id,block_id,district_id)
        if livestock:
            secondary_livestock = round(sum([float(item['value']) for item in livestock]), 2)
        crops = BudgetData.get_crops_consumption(panchayat_id,block_id,district_id)
        if crops:
            secondary_crop = round(sum([float(item['value']) for item in crops]), 2)
            
        total_secondary_demand = secondary_human + secondary_livestock + secondary_crop + secondary_industry
        secondary_demand = {'human':secondary_human, 'livestock':secondary_livestock, 'crop':secondary_crop, 'industry':secondary_industry,'total':total_secondary_demand}
        return secondary_demand
    
    @classmethod
    def get_secondary_supply(cls,panchayat_id,block_id,district_id,state_id):
        secondary_surface = 0
        secondary_ground = 0
        secondary_runoff = 0
        secondary_transfer = 0
        surface = BudgetData.get_surface_supply(panchayat_id,block_id,district_id)
        if surface:
            secondary_surface = round(sum([float(item['value']) for item in surface]), 2)
        ground = BudgetData.get_ground_supply(panchayat_id,block_id,district_id)
        if ground:
            secondary_ground = [item['value'] for item in ground if item['name'] == 'extraction'][0]
        runoff = BudgetData.get_runoff(panchayat_id,block_id,district_id)
        if runoff:
            secondary_runoff = round(sum([float(item['supply']) for item in runoff]), 2)
        transfer = BudgetData.get_water_transfer(panchayat_id,block_id,district_id)
        if transfer:
            secondary_transfer = round(sum([float(item['entity_value']) for item in transfer]), 2)
            
        total_secondary_supply = secondary_surface + secondary_ground + secondary_runoff + secondary_transfer
        secondary_supply = {'surface':secondary_surface, 'ground':secondary_ground, 'runoff':secondary_runoff, 'transfer':secondary_transfer,'total':total_secondary_supply}
        return secondary_supply
    
    @classmethod
    def get_primary_demand(cls,panchayat_id,block_id,district_id,state_id):
        human_consumption = 0
        livestock_consumption = 0
        crop_consumption = 0
        industry_consumption = 0
        bt_id = BlockData.get_bt_id(panchayat_id=panchayat_id,block_id=block_id, district_id=district_id, state_id=state_id)
        if bt_id:
            human = BlockPop.get_block_population_data(bt_id)
            entity_count = sum([float(item['entity_count']) for item in human]) if human else 0
            filtered_human = [item for item in human if item['entity_count'] > 0] if human else []
            is_approved = all(row['is_approved'] for row in filtered_human if row['is_approved'] is not None)
            if not entity_count or not is_approved:
                human = BudgetData.get_human_consumption(panchayat_id,block_id,district_id)
                human_consumption = round(sum([float(item['value']) for item in human]), 2)
                primary_human = round(sum([float(item['count']) for item in human]), 2)
                human = {'consumption': human_consumption, 'count': primary_human,'source': False}
            else:
                primary_human = round(sum([float(item['entity_count']) for item in human]), 2)
                human_consumption = round(cls.litre_to_hectare_meters((int(primary_human) * cls.RURAL_CONSUMPTION * cls.DECADAL_GROWTH * cls.NUMBER_OF_DAYS * cls.WATER_LOSS)),2)
                human = {'consumption': human_consumption, 'count': primary_human,'source': True}
                
            livestock = BlockLivestock.get_block_livestock_data(bt_id)
            entity_count = sum([float(item['entity_count']) for item in livestock]) if livestock else 0
            filtered_livestock = [item for item in livestock if item['entity_count'] > 0] if livestock else []
            is_approved = all(row['is_approved'] for row in filtered_livestock if row['is_approved'] is not None)
            if not entity_count or not is_approved:
                livestock = BudgetData.get_livestock_consumption(panchayat_id,block_id,district_id)
                livestock_consumption = round(sum([float(item['value']) for item in livestock]), 2)
                primary_livestock = round(sum([float(item['count']) for item in livestock]), 2)
                livestock = {'consumption': livestock_consumption, 'count': primary_livestock,'source': False}
            else:
                for item in livestock:
                    item['entity_consumption'] = round(cls.litre_to_hectare_meters(
                        float(item['entity_count']) * float(item['coefficient']) 
                        * cls.NUMBER_OF_DAYS),2)
                primary_livestock = round(sum([float(item['entity_count']) for item in livestock]), 2)
                livestock_consumption = round(sum([float(item['entity_consumption']) for item in livestock]), 2)
                livestock = {'consumption': livestock_consumption, 'count': primary_livestock,'source': True}
                
            crops = BlockCrop.get_block_crop_data(bt_id)
            entity_count = sum([float(item['entity_count']) for item in crops]) if crops else 0
            filtered_crops = [item for item in crops if item['entity_count'] > 0] if crops else []
            is_approved = all(row['is_approved'] for row in filtered_crops if row['is_approved'] is not None)
            if not entity_count or not is_approved:
                crops = BudgetData.get_crops_consumption(panchayat_id,block_id,district_id)
                crop_consumption = round(sum([float(item['value']) for item in crops]), 2)
                primary_crop = round(sum([float(item['count']) for item in crops]), 2)
                crops = {'consumption': crop_consumption, 'count': primary_crop,'source': False}
            else:
                for item in crops:
                    item['entity_consumption'] = round(float(item['entity_count']) * float(item['coefficient']),2)
                primary_crop = round(sum([float(item['entity_count']) for item in crops]), 2)
                crop_consumption = round(sum([float(item['entity_consumption']) for item in crops]), 2)
                crops = {'consumption': crop_consumption, 'count': primary_crop,'source': True}
                
            industries = BlockIndustry.get_block_industry_data(bt_id)
            if industries:
                primary_industry = round(sum([float(item['entity_count']) for item in industries]), 2)
                industry_consumption = round(sum([float(item['entity_consumption']) for item in industries]), 2)
                industry = {'consumption': industry_consumption, 'count': primary_industry,'source': True}
                
        total_primary_demand = human_consumption + livestock_consumption + crop_consumption + industry_consumption
        primary_demand = {'human':human, 'livestock':livestock, 'crop':crops, 'industry':industry,'total':total_primary_demand}
        return primary_demand

    
    @classmethod
    def get_primary_supply(cls,panchayat_id,block_id,district_id,state_id):
        surface_consumption = 0
        primary_ground = 0
        primary_runoff = 0
        transfer_consumption = 0
        bt_id = BlockData.get_bt_id(panchayat_id=panchayat_id,block_id=block_id, district_id=district_id, state_id=state_id)
        if bt_id:
            surface = BlockWaterbody.get_block_waterbody_data(bt_id)
            entity_count = sum([float(item['entity_count']) for item in surface]) if surface else 0
            filtered_surface = [item for item in surface if item['entity_count'] > 0] if surface else []
            is_approved = all(row['is_approved'] for row in filtered_surface if row['is_approved'] is not None)
            if not entity_count or not is_approved:
                surface = BudgetData.get_surface_supply(panchayat_id,block_id,district_id)
                primary_surface = round(sum([float(item['count']) for item in surface]), 2)
                surface_consumption = round(sum([float(item['value']) for item in surface]), 2)
                surface = {'consumption': surface_consumption, 'count': primary_surface,'source': False}
            else:
                primary_surface = round(sum([float(item['entity_count']) for item in surface]), 2)
                surface_consumption = round(sum([float(item['entity_consumption']) for item in surface]), 2)
                surface = {'consumption': surface_consumption, 'count': primary_surface,'source': True}

            ground = BlockGround.get_block_groundwater_data(bt_id)
            is_approved = ground['is_approved'] if ground else False
            if not is_approved:
                ground = BudgetData.get_ground_supply(panchayat_id,block_id,district_id)
                primary_ground = [item['value'] for item in ground if item['name'] == 'extraction'][0]
                ground = {'consumption': primary_ground, 'count': 1,'source': False}
            else:
                primary_ground = round(float(ground['extraction']), 2)
                ground = {'consumption': primary_ground, 'count': 1,'source': True}
                
            runoff,is_approved = cls.get_primary_runoff(panchayat_id, block_id, district_id)
            if runoff:
                primary_runoff = round(sum([float(item['supply']) for item in runoff]), 2)
                if not is_approved:
                    runoff = {'consumption': primary_runoff, 'count': 1,'source': False}
                else:  
                    runoff = {'consumption': primary_runoff, 'count': 1,'source': True}
                
            transfer = BudgetData.get_water_transfer(panchayat_id,block_id,district_id)
            if transfer:
                primary_transfer = round(sum([float(item['entity_value']) for item in transfer]), 2)
                transfer = {'consumption': primary_transfer, 'count': 1,'source': True}
            
        total_primary_supply = surface_consumption + primary_ground + primary_runoff + transfer_consumption
        primary_supply = {'surface':surface, 'ground':ground, 'runoff':runoff, 'transfer':transfer,'total':total_primary_supply}
        return primary_supply
    
    @classmethod
    def get_primary_secondary_budget(cls,panchayat_id,block_id,district_id,state_id=2):
        primary_demand = cls.get_primary_demand(panchayat_id,block_id,district_id,state_id)
        secondary_demand = cls.get_secondary_demand(panchayat_id,block_id,district_id,state_id)
        primary_supply = cls.get_primary_supply(panchayat_id,block_id,district_id,state_id)
        secondary_supply = cls.get_secondary_supply(panchayat_id,block_id,district_id,state_id)
        
        human = {'entity':'human','primary':primary_demand['human'], 'secondary':secondary_demand['human']}
        livestock = {'entity':'livestock','primary':primary_demand['livestock'], 'secondary':secondary_demand['livestock']}
        crops = {'entity':'crops','primary':primary_demand['crop'], 'secondary':secondary_demand['crop']}
        industry = {'entity':'industry','primary':primary_demand['industry'], 'secondary':secondary_demand['industry']}
        surface = {'entity':'surface','primary':primary_supply['surface'], 'secondary':secondary_supply['surface']}
        ground = {'entity':'ground','primary':primary_supply['ground'], 'secondary':secondary_supply['ground']}
        runoff = {'entity':'runoff','primary':primary_supply['runoff'], 'secondary':secondary_supply['runoff']}
        transfer = {'entity':'transfer','primary':primary_supply['transfer'], 'secondary':secondary_supply['transfer']}
        total_demand = {'entity':'demand','primary':primary_demand['total'], 'secondary':secondary_demand['total']}
        total_supply = {'entity':'supply','primary':primary_supply['total'], 'secondary':secondary_supply['total']}
        final_budget = {'entity':'budget','primary':primary_supply['total']-primary_demand['total'], 'secondary':secondary_supply['total']-secondary_demand['total']}
        demand = [human, livestock, crops, industry]
        supply = [surface, ground, runoff, transfer]
        budget = [total_demand, total_supply, final_budget]
        return demand,supply,budget
    
    @classmethod
    def get_primary_runoff(cls, panchayat_id, block_id, district_id, state_id=2):
        bt_id = BlockData.get_bt_id(panchayat_id=panchayat_id,block_id=block_id, district_id=district_id, state_id=state_id)
        if bt_id:
            rainfall_data = BlockRainfall.get_rainfall_data(bt_id)
            is_approved_rainfall = False
            if rainfall_data:
                is_approved_rainfall =all(row['is_approved'] for row in rainfall_data if row['is_approved'] is not None)
            if not is_approved_rainfall:
                rainfall_data = BudgetData.get_rainfall(panchayat_id,block_id, district_id)
            if rainfall_data:
                rainfall_in_mm = float(sum(item['actual'] for item in rainfall_data))
                if rainfall_in_mm > 1500:
                    rainfall_in_mm = 1500
                runoff_data = StrangeTable.get_runoff_by_rainfall(rainfall_in_mm)
                lulc_data = BlockLULC.get_block_lulc_data(bt_id)
                is_approved_lulc = False
                if lulc_data:
                    is_approved_lulc = all(row['is_approved'] for row in lulc_data if row['is_approved'] is not None)
                if not is_approved_lulc:
                    lulc_data = LULCCensus.get_census_data_lulc(panchayat_id,block_id, district_id)
                if lulc_data:
                    runoff_array = []
                    for key,value in runoff_data[0].items():
                        if not key=='rainfall_in_mm':
                            catchment_area = [item['catchment_area'] for item in lulc_data if item['catchment'] == key.lower()][0]
                            runoff_yield = round((value/10) * rainfall_in_mm, 2)
                            catchment_yield = round(catchment_area * runoff_yield, 2)
                            item = {'catchment': key, 
                                    'runoff': value, 
                                    'runoff_yield': runoff_yield, 
                                    'supply': round(cls.cubic_meter_to_hectare_meters(catchment_yield),2)}
                            runoff_array.append(item)
                    bg_colors = cls.COLORS
                    runoff = [{**item, 'background': bg} for item, bg in zip(runoff_array, bg_colors)]
                    return runoff,is_approved_lulc and is_approved_rainfall
        return None,False
