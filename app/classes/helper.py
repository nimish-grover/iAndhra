from itertools import cycle
from flask import url_for

from app.classes.block_or_census import BlockOrCensus
from app.models.block_progress import BlockProgress
from app.models.users import User


class HelperClass():
    COLORS = ['#5470c6','#91cc75','#fac858','#ee6666','#73c0de','#3ba272','#fc8452','#9a60b4']

    @classmethod
    def get_version(cls):
        with open('version.txt', 'r') as file:
            version = file.read().strip()
        return version
    
    @classmethod
    def aggregate_by_panchayat(cls,data):
        # Create a dictionary to store aggregated panchayat data
        panchayat_map = {}
        
        # Process each village entry
        for village in data:
            panchayat_id = village['panchayat_id']
            
            # If this panchayat hasn't been seen before, initialize it
            if panchayat_id not in panchayat_map:
                panchayat_map[panchayat_id] = {
                    'panchayat_id': panchayat_id,
                    'panchayat_name': village['panchayat_name'],
                    'block_id': village['block_id'],
                    'block_name': village['block_name'],
                    'district_id': village['district_id'],
                    'district_name': village['district_name'],
                    'district_short_name': village['district_short_name'],
                    'total_supply': 0,
                    'total_demand': 0,
                    'budget': 0,
                    'villages': []
                }
            
            # Aggregate the values
            panchayat_map[panchayat_id]['total_supply'] += village['total_supply']
            panchayat_map[panchayat_id]['total_demand'] += village['total_demand']
            panchayat_map[panchayat_id]['budget'] += village['budget']
            
            # Add this village to the list
            panchayat_map[panchayat_id]['villages'].append({
                'id': village['id'],
                'village_id': village['village_id'],
                'village_name': village['village_name'],
                'total_supply': village['total_supply'],
                'total_demand': village['total_demand'],
                'budget': village['budget']
            })
        
        # Convert the map to a list
        return list(panchayat_map.values())
    
    @classmethod
    def get_budget_data(cls):
        progress_data = BlockProgress.get_village_progress()
        budget_array = []
        for idx,data in enumerate(progress_data):
            demand_side = BlockOrCensus.get_demand_side_data(data['village_id'],data['panchayat_id'],data['block_id'],data['district_id'])
            total_demand = int(sum([item['water_value'] for item in demand_side]))
            supply_side = BlockOrCensus.get_supply_side_data(data['village_id'],data['panchayat_id'],data['block_id'],data['district_id'])
            total_supply = int(sum([item['water_value'] for item in supply_side]))
            budget = int(total_supply - total_demand)
            
            budget_array.append({'id':idx+1,'block_id':data['block_id'],'district_id':data['district_id'],
                            'district_short_name':data['district_short_name'],'district_name':data['district_name'],
                            'block_name':data['block_name'],'total_demand':total_demand,'village_name':data['village_name'],
                            'total_supply':total_supply,'budget':budget,'village_id':data['village_id'],
                            'panchayat_id':data['panchayat_id'],'panchayat_name':data['panchayat_name']})
        budget_array = cls.aggregate_by_panchayat(budget_array)
        budget_array = sorted(budget_array, key=lambda x: x["budget"])
        return budget_array
    
    @classmethod
    def get_panchayat_progress(cls):
        progress_data = BlockProgress.get_panchayat_progress()
        return progress_data
    
    @classmethod
    def get_chart_data(cls):
        progress_data = BlockProgress.get_district_progress()
        chart_data = []
        
        color_cycle = cycle(cls.COLORS)
        for item in progress_data:
            if item['completed_percentage']:
                color = next(color_cycle)
                chart_data.append({'completed':item['completed_percentage'],'percentage':str(item['completed_percentage'])+'%',
                                'color':color,'district_name':item['district_name'],
                                'district_short_name':item['district_short_name']})
        chart_data = sorted(chart_data, key=lambda x: x["completed"])
        return chart_data
    
    @classmethod
    def get_card_data(cls):
        panchayat_progress = BlockProgress.get_panchayat_progress()
        panchayat_in_progress = len(panchayat_progress)
        panchayat_completed = sum(1 for item in panchayat_progress if int(item.get('completed_percentage')) == 100)
        user_status = User.get_active_count()
        return [
            {'title': 'Users Active', 'value': cls.format_value(user_status['active_users']), 'icon': 'fa-user-gear'},
            {'title': 'Users Registered', 'value': cls.format_value(user_status['active_users']+user_status['inactive_users']), 'icon': 'fa-user-check'},
            {'title': 'Panchayats In-Progress', 'value': cls.format_value(panchayat_in_progress), 'icon': 'fa-gears'},
            {'title': 'Panchayats Completed', 'value': cls.format_value(panchayat_completed), 'icon': 'fa-list-check'}]
    
    @classmethod
    def update_user_panchayat(cls,user_id,panchayat_ids,block_id,district_id):
        user = User.get_by_id(user_id)
        panchayat_arr = [int(item) for item in panchayat_ids.split(',')]
        user.panchayat_id = panchayat_arr
        user.update_db()
        panchayat_check = User.get_user_panchayat_by_block(block_id)
        for item in panchayat_check:
            if item['user_id'] != user_id:
                panchayat_check_arr = item['panchayat_ids']
                for id in panchayat_check_arr:
                    if id in panchayat_arr:
                        user_duplicate_id = item['user_id']
                        panchayat_check_arr.remove(id)
                if user_duplicate_id:
                    user_duplicate = User.get_by_id(user_duplicate_id)
                    user_duplicate.panchayat_id = panchayat_check_arr
                    user_duplicate.update_db()
        return True
        
        
    def format_value(value):
        if value < 10:
            return f"{value:02d}"
        return str(value)
    
    def indian_number_format(value):
        """
        Formats a number in the Indian number system (e.g., 12,34,567 or 12,34,567.89).
        Handles input as str or numeric type. Rounds to 2 decimal places.
        """
        # Check if value is a string
        if isinstance(value, str):
            try:
                value = float(value)  # Convert to float
            except ValueError:
                raise TypeError(f"Value must be a number or a numeric string, got '{value}'")
        
        # Handle negative values
        is_negative = value < 0
        value = abs(value)  # Work with absolute value for formatting
        
        # Round the value to 2 decimal places
        value = round(value, 2)
        
        # Format the number to ensure it has decimal precision
        value_str = f"{value:.2f}"
        integer_part, decimal_part = value_str.split(".")
        
        # Reverse the integer part for easier grouping
        integer_part = integer_part[::-1]
        
        # Format integer part in Indian number system
        parts = []
        for i in range(len(integer_part)):
            if i == 3 or (i > 3 and (i - 3) % 2 == 0):  # Add a comma after 3 digits, then every 2 digits
                parts.append(",")
            parts.append(integer_part[i])
        
        # Reverse back the formatted integer part
        formatted_integer = "".join(parts)[::-1]
        
        # Add the negative sign back if necessary
        if is_negative:
            formatted_integer = "-" + formatted_integer

        # Omit decimal part if it is 0
        if int(decimal_part) == 0:
            return formatted_integer
        else:
            return f"{formatted_integer}.{decimal_part}"

    def get_supply_menu():
        return [
            { "route" : url_for('.status'), "label":"back", "icon":"fa-solid fa-left-long"},
            { "route" : url_for('.surface'), "label":"surface", "icon":"fa-solid fa-water"},
            { "route" : url_for('.ground'), "label":"ground", "icon":"fa-solid fa-arrow-up-from-ground-water"},
            { "route" : url_for('.lulc'), "label":"lulc", "icon":"fa-solid fa-cloud-showers-water"},
            { "route" : url_for('.rainfall'), "label":"rainfall", "icon":"fa-solid fa-cloud-rain"},
        ]

    def get_demand_menu():
        return [
            { "route" : url_for('.status'), "label":"back", "icon":"fa-solid fa-left-long"},
            { "route" : url_for('.human'), "label":"human", "icon":"fa-solid fa-people-roof"},
            { "route" : url_for('.livestocks'), "label":"livestock", "icon":"fa-solid fa-paw"},
            { "route" : url_for('.crops'), "label":"crops", "icon":"fa-brands fa-pagelines"},
            { "route" : url_for('.industries'), "label":"industries", "icon":"fa-solid fa-industry"},
        ]
    
    def get_main_menu():
        return [
            { "route" : url_for('mobile.index'), "label":"home", "icon":"fa-solid fa-house"},
            { "route" : url_for('desktop.status'), "label":"status", "icon":"fa-solid fa-list-check"},
            { "route" : url_for('desktop.human'), "label":"demand", "icon":"fa-solid fa-chart-line"},
            { "route" : url_for('desktop.surface'), "label":"supply", "icon":"fa-solid fa-glass-water-droplet"},
            { "route" : url_for('desktop.transfer'), "label":"transfer", "icon":"fa-solid fa-arrow-right-arrow-left"},
        ]
    
    def get_admin_menu():
        return [
            { "route" : url_for('mobile.index'), "label":"home", "icon":"fa-solid fa-house"},
            { "route" : url_for('.dashboard'), "label":"dashboard", "icon":"fa-solid fa-gauge"},
            { "route" : url_for('.approve'), "label":"approve", "icon":"fa-solid fa-list-check"},
            { "route" : url_for('.progress'), "label":"progress", "icon":"fa-solid fa-bars-progress"},
            # { "route" : url_for('.budget'), "label":"budget", "icon":"fa-solid fa-scale-unbalanced"}
        ]
    
    def get_breadcrumbs(payload):
        """
        Generate breadcrumb navigation based on the current payload.

        Returns:
            list: Breadcrumbs for the current context.
        """
        return [
            {'name': payload['district_short_name'], 'href': '#'},
            {'name': payload['block_name'], 'href': '#'},
            {'name': payload['panchayat_name'], 'href': '#'}]