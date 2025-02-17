from itertools import cycle
from flask import url_for

from app.models.block_progress import BlockProgress
from app.models.users import User


class HelperClass():
    COLORS = ['#5470c6','#91cc75','#fac858','#ee6666','#73c0de','#3ba272','#fc8452','#9a60b4']

    @classmethod
    def get_dashboard_menu(cls):
        progress_data = BlockProgress.get_all_villages_status()
        chart_data = []
        
        color_cycle = cycle(cls.COLORS)
        for item in progress_data:
            if item['bt_id']:
                color = next(color_cycle)
                chart_data.append({'panchayat_name':item['panchayat_name'], 'completed':item['completed'],
                                'block_name':item['block_name'],'percentage':str(item['completed'])+'%',
                                'color':color,'district_name':item['district_name'],'category_id':item['category_id'],
                                'district_short_name':item['district_short_name'],'bt_id':item['bt_id']})
        return chart_data
    
    @classmethod
    def get_chart_data(cls):
        progress_data = BlockProgress.get_all_districts_status()
        chart_data = []
        
        color_cycle = cycle(cls.COLORS)
        for item in progress_data:
            if item['completed']:
                color = next(color_cycle)
                chart_data.append({'completed':item['completed'],'percentage':str(item['completed'])+'%',
                                'color':color,'district_name':item['district_name'],'category_id':item['category_id'],
                                'district_short_name':item['district_short_name'],'bt_id':item['bt_id']})
        return chart_data
    
    @classmethod
    def get_card_data(cls,chart_data):
        completed_blocks = sum(1 for item in chart_data if item.get('completed') == 100)
        user_status = User.get_active_count()
        return [
            {'title': 'Users Active', 'value': cls.format_value(user_status['active_users']), 'icon': 'fa-user-gear'},
            {'title': 'Users Registered', 'value': cls.format_value(user_status['active_users']+user_status['inactive_users']), 'icon': 'fa-user-check'},
            {'title': 'Panchayats In-Progress', 'value': cls.format_value(len(chart_data)-completed_blocks), 'icon': 'fa-gears'},
            {'title': 'Panchayats Completed', 'value': cls.format_value(completed_blocks), 'icon': 'fa-list-check'}]
    
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
            { "route" : url_for('.dashboard'), "label":"dashboard", "icon":"fa-solid fa-gauge"},
            { "route" : url_for('.approve'), "label":"approve", "icon":"fa-solid fa-list-check"},
            { "route" : url_for('.progress'), "label":"progress", "icon":"fa-solid fa-bars-progress"}
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
            {'name': payload['panchayat_name'], 'href': '#'},
            {'name': payload['village_name'], 'href': '#'}
        ]