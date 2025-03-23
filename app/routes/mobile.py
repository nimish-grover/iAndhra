from flask import Blueprint, json, jsonify, make_response, redirect, render_template, request, session, url_for
from flask_login import current_user
from app.classes.helper import HelperClass
from app.classes.block_or_census import BlockOrCensus
from app.classes.budget_data import BudgetData
from app.models import TerritoryJoin
from app.models.districts import District
from app.models.territory import TerritoryJoin
from app.models.users import User


blp = Blueprint("mobile","mobile")

@blp.route('/')
def splash():
    return render_template("splash_screen.html")

@blp.route('/index', methods=['POST','GET'])
def index():
    if request.method == 'POST':
        json_data = request.json
        if 'payload' in session:
            session['payload'] = ''
        json_data['district_short_name'] = District.get_short_name(int(json_data['district_id']))
        payload = json.dumps(json_data)
        session['payload'] = payload
        if current_user.is_authenticated:
            return json.dumps(url_for('desktop.status'))
        return json.dumps(url_for('.home'))
    if current_user.is_authenticated:
        if current_user.isAdmin:
            districts = TerritoryJoin.get_districts()
        else:
            districts = District.get_districts_by_id(current_user.district_id)
    else:
        districts = TerritoryJoin.get_districts()
    return render_template("mobile/index.html", districts=districts)

# @blp.route("/villages", methods=['POST'])
# def villages():
#     json_data = request.json
#     if json_data is not None:
#         panchayat_id = int(json_data['panchayat_id'])
#     else:
#         return make_response('', 400)
#     villages = TerritoryJoin.get_villages(panchayat_id)
#     if villages:
#         return villages
#     else:
#         return make_response('', 400)

@blp.route("/panchayats", methods=['POST'])
def panchayats():
    json_data = request.json
    if json_data is not None:
        block_id = int(json_data['block_id'])
    else:
        return make_response('', 400)
    panchayats = TerritoryJoin.get_panchayats(block_id)
    checked_panchayats = User.get_panchayat_id_by_block(block_id)
    updated_panchayats = [
        {**item, "disabled": True} if item["id"] in checked_panchayats else item 
        for item in panchayats
    ]
    if current_user.is_authenticated:
        if not current_user.isAdmin:
            user_panchayats = User.get_panchayat_id_by_block(current_user.block_id,current_user.id)
            filtered_panchayats = [panchayat for panchayat in panchayats if panchayat['id'] in user_panchayats]
            # filtered_panchayats = [panchayat for panchayat in panchayats if panchayat['id'] == current_user.panchayat_id]
            return filtered_panchayats
    if updated_panchayats:
        return updated_panchayats
    else:
        return make_response('', 400)
    
@blp.route("/user_panchayats",methods=['POST'])
def user_panchayats():
    json_data = request.json
    if json_data is not None:
        block_id = int(json_data['block_id'])
    else:
        return make_response('', 400)
    panchayats = TerritoryJoin.get_panchayats(block_id)
    user_id = session.get('user_data')['id']
    checked_panchayats = User.get_panchayat_id_by_block(block_id,user_id)
    updated_panchayats = [
        {**item, "disabled": True} if item["id"] in checked_panchayats else item 
        for item in panchayats
    ]
    if updated_panchayats:
        return updated_panchayats
    else:
        return make_response('', 400)
    
@blp.route("/blocks", methods=['POST'])
def blocks():
    json_data = request.json
    if json_data is not None:
        district_id = int(json_data['district_id'])
    else:
        return make_response('', 400)
    blocks = TerritoryJoin.get_blocks(district_id)
    if current_user.is_authenticated:
        if not current_user.isAdmin:
            filtered_blocks = [block for block in blocks if block['id'] == current_user.block_id]
            return filtered_blocks
    if blocks:
        return blocks
    else:
        return make_response('', 400)


@blp.route('/home')
def home():
    payload = session.get('payload')
    if not payload:
        return redirect(url_for('.index'))
    else:
        payload = json.loads(payload)
    demand_side = BlockOrCensus.get_demand_side_data(payload['panchayat_id'],payload['block_id'], payload['district_id'])
    supply_side = BlockOrCensus.get_supply_side_data(payload['panchayat_id'],payload['block_id'], payload['district_id'])
    budget = BlockOrCensus.get_water_budget_data(payload['panchayat_id'],payload['block_id'], payload['district_id'])
    budget_data = []
    budget_data.append(demand_side)
    budget_data.append(supply_side)
    budget_data.append(budget)
    return render_template("mobile/home.html", 
                           breadcrumbs = get_breadcrumbs(payload),
                           demand_side = budget_data[0],
                           supply_side = budget_data[1],
                           water_budget = budget_data[2],
                           menu = get_main_menu(),
                           chart_data = json.dumps(budget_data),
                           toggle_labels=['chart', 'table'])

# @blp.route('/home')
# def home():
#     payload = session.get('payload')
#     if not payload:
#         return redirect(url_for('.index'))
#     else:
#         payload = json.loads(payload)
#     demand_side = BudgetData.get_demand_side(payload['block_id'], payload['district_id'])
#     supply_side = BudgetData.get_supply_side(payload['block_id'], payload['district_id'], payload['state_id'])
#     budget = BudgetData.get_water_budget(payload['block_id'], payload['district_id'], payload['state_id'])
#     budget_data = []
#     budget_data.append(demand_side)
#     budget_data.append(supply_side)
#     budget_data.append(budget)
#     return render_template("mobile/home.html", 
#                            breadcrumbs = get_breadcrumbs(payload),
#                            demand_side = budget_data[0],
#                            supply_side = budget_data[1],
#                            water_budget = budget_data[2],
#                            menu = get_main_menu(),
#                            chart_data = json.dumps(budget_data),
#                            toggle_labels=['chart', 'table'])

@blp.route('/human')
def human():
    payload = session.get('payload')
    if not payload:
        return redirect(url_for('.index'))
    else:
        payload = json.loads(payload)
    human, is_approved = BlockOrCensus.get_human_data(payload['panchayat_id'],payload['block_id'],payload['district_id'])
    return render_template('mobile/demand/human.html',
        is_approved = is_approved, 
        source='Census 2011',
        human = human,
        chart_data= json.dumps(human),
        toggle_labels= ['chart', 'table'],
        breadcrumbs= get_breadcrumbs(payload), 
        menu= get_demand_menu())
# @blp.route('/human')
# def human():
#     """
#     Handle human demand route.
#     """
#     return render_demand_template(
#         "mobile/demand/human.html",
#         demand_function=BudgetData.get_human_consumption,
#         template_data_key='human'
    # )

@blp.route('/livestocks')
def livestocks():
    payload = session.get('payload')
    if not payload:
        return redirect(url_for('.index'))
    else:
        payload = json.loads(payload)
    livestock, is_approved = BlockOrCensus.get_livestock_data(payload['panchayat_id'],payload['block_id'],payload['district_id'])  
    return render_template('mobile/demand/livestocks.html',
        is_approved = is_approved, 
        source = 'Livestock Census 2019',
        livestocks = livestock,
        chart_data= json.dumps(livestock),
        toggle_labels= ['chart', 'table'],
        breadcrumbs= get_breadcrumbs(payload), 
        menu= get_demand_menu())  
# @blp.route('/livestocks')
# def livestocks():
#     return render_demand_template(
#         "mobile/demand/livestocks.html",
#         demand_function=BudgetData.get_livestock_consumption,
#         template_data_key='livestocks'
#     )

@blp.route('/crops')
def crops():
    payload = session.get('payload')
    if not payload:
        return redirect(url_for('.index'))
    else:
        payload = json.loads(payload)
    crops, is_approved = BlockOrCensus.get_crop_data(payload['panchayat_id'],payload['block_id'],payload['district_id']) 
    return render_template('mobile/demand/crops.html',
        is_approved = is_approved, 
        source = 'Crop Census 2019 (DES)', #https://data.desagri.gov.in/website/crops-apy-report-web
        crops = crops,
        chart_data= json.dumps(crops),
        toggle_labels= ['chart', 'table'],
        breadcrumbs= get_breadcrumbs(payload), 
        menu= get_demand_menu())

# @blp.route('/crops')
# def crops():
#     return render_demand_template(
#         "mobile/demand/crops.html",
#         demand_function=BudgetData.get_crops_consumption,
#         template_data_key='crops'
#     )

@blp.route('/industry')
def industry():
    payload = session.get('payload')
    if not payload:
        return redirect(url_for('.index'))
    else:
        payload = json.loads(payload)
    industry_demand, is_approved = BlockOrCensus.get_industry_data(payload['panchayat_id'],payload['block_id'], payload['district_id'])
    has_value = sum(item['count'] for item in industry_demand)
    if is_approved:
            source = 'The Industrial Water demand is reported nil by the block' 
    else:
        source = 'The Industrial Water demand is reported nil by the block' if has_value else 'Industry demand input is awaited.'
    return render_template("mobile/demand/industry.html",
                        subtitle = '(in Ha M)' if is_approved else 'There are no industry in this Village',
                        industries = industry_demand if has_value else None, 
                        source = source,
                        is_approved = is_approved,
                        chart_data = json.dumps(industry_demand),
                        breadcrumbs= get_breadcrumbs(payload), 
                        menu= get_demand_menu(),
                        toggle_labels=['chart', 'table'])


# @blp.route('/industry')
# def industry():
#     payload = session.get('payload')
#     if not payload:
#         return redirect(url_for('.index'))
#     else:
#         payload = json.loads(payload)
#     industry_demand = BudgetData.get_industry_demand(payload['block_id'], payload['district_id'], payload['state_id'])
#     has_value = sum(item['count'] for item in industry_demand)
#     return render_template("mobile/demand/industry.html",
#                         subtitle = '(in Ha M)' if has_value > 0 else 'There are no industry in this block',
#                         industries = industry_demand, 
#                         chart_data = json.dumps(industry_demand),
#                         breadcrumbs= get_breadcrumbs(payload), 
#                         menu= get_demand_menu(),
#                         toggle_labels=['chart', 'table'])

@blp.route('/surface')
def surface():
    payload = session.get('payload')
    if not payload:
        return redirect(url_for('.index'))
    else:
        payload = json.loads(payload)
    surface_water_supply, is_approved = BlockOrCensus.get_surface_data(payload['panchayat_id'],payload['block_id'], payload['district_id'])
    waterbodies=[]
    if surface_water_supply:
        waterbodies = sorted(surface_water_supply, key = lambda x: x['value'], reverse=True)
    return render_template('mobile/supply/surface.html',
                        is_approved = is_approved, 
                        source = 'India’s First waterbodies census 2019',  
                        waterbodies= waterbodies,
                        chart_data= json.dumps(surface_water_supply),
                        toggle_labels= ['chart', 'table'],
                        breadcrumbs=get_breadcrumbs(payload), 
                        menu=get_supply_menu()
                        )

# @blp.route('/surface')
# def surface():
#     return render_supply_template(
#         "mobile/supply/surface.html",
#         supply_function=BudgetData.get_surface_supply,
#         template_data_key='waterbodies'
    # )

@blp.route('/ground')
def ground():
    payload = session.get('payload')
    if not payload:
        return redirect(url_for('.index'))
    else:
        payload = json.loads(payload)
    ground_water_supply, is_approved = BlockOrCensus.get_ground_data(payload['panchayat_id'],
                                                payload['block_id'],
                                                payload['district_id'])
    
    return render_template('mobile/supply/ground.html',
                        is_approved = is_approved,  
                        source = 'INDIA-Groundwater Resource Estimation System (IN-GRES)', 
                        groundwater= ground_water_supply,
                        chart_data= json.dumps(ground_water_supply),
                        toggle_labels= ['chart', 'table'],
                        breadcrumbs=get_breadcrumbs(payload), 
                        menu=get_supply_menu())

# @blp.route('/ground')
# def ground():
#     return render_supply_template(
#         "mobile/supply/ground.html",
#         supply_function=BudgetData.get_ground_supply,
#         template_data_key='groundwater'
#     )

@blp.route('/rainfall')
def rainfall():
    payload = session.get('payload')
    if not payload:
        return redirect(url_for('.index'))
    else:
        payload = json.loads(payload)
    rainfall_data, is_approved = BlockOrCensus.get_rainfall_data(payload['panchayat_id'],payload['block_id'], payload['district_id'])
    if len(rainfall_data)!=12:
        rainfall_data=None
    return render_template("mobile/supply/rainfall.html", 
                           source='India- Water Resource Information System (WRIS)',
                           is_approved = is_approved,
                           monthwise_rainfall = rainfall_data,
                           chart_data = json.dumps(rainfall_data),
                           breadcrumbs = get_breadcrumbs(payload),
                           menu= get_supply_menu(),
                           toggle_labels=['chart', 'table'])

@blp.route('/runoff')
def runoff():
    payload = session.get('payload')
    if not payload:
        return redirect(url_for('.index'))
    else:
        payload = json.loads(payload)
    runoff_data, is_approved = BlockOrCensus.get_runoff_data(payload['panchayat_id'],payload['block_id'], payload['district_id'])
    return render_template("mobile/supply/runoff.html", 
                           is_approved = is_approved,
                           source="Strange's Table",
                           catchments=runoff_data,
                           chart_data = json.dumps(runoff_data),
                           breadcrumbs = get_breadcrumbs(payload),
                           menu= get_supply_menu(),
                           toggle_labels=['chart', 'table'])

def render_supply_template(template, supply_function, template_data_key):
    payload = session.get('payload')
    if not payload:
        return redirect(url_for('.index'))
    else:
        payload = json.loads(payload)
    # Fetch supply data
    chart_data = supply_function(payload['block_id'], payload['district_id'])
    toggle_labels=['chart', 'table']

    context = {
        template_data_key: chart_data,
        "chart_data": json.dumps(chart_data),
        "toggle_labels": toggle_labels,
        "breadcrumbs": get_breadcrumbs(payload), 
        "menu": get_supply_menu()
    }

    return render_template(template, **context)


def render_demand_template(template, demand_function, template_data_key):
    """
    Render a demand-related template with shared logic for retrieving demand data and rendering the page.

    Args:
        template (str): Template path to render.
        demand_function (callable): Function to fetch demand data (e.g., WaterBudget.get_human_demand).
        toggle_labels (list): Labels for toggling chart/table views.
        template_data_key (str): Key for the primary data object in the template context.

    Returns:
        Rendered HTML template or a redirect if session data is missing.
    """
    payload = session.get('payload')
    if not payload:
        return redirect(url_for('.index'))
    else:
        payload = json.loads(payload)
    # block, district = payload['block_id'], payload['district_id']

    # Fetch demand data
    chart_data = demand_function(payload['block_id'], payload['district_id'])

    toggle_labels=['chart', 'table']
    # Prepare template context
    context = {
        template_data_key: chart_data,
        "chart_data": json.dumps(chart_data),
        "toggle_labels": toggle_labels,
        "breadcrumbs": get_breadcrumbs(payload), 
        "menu": get_demand_menu()
    }

    return render_template(template, **context)

@blp.route('/change-theme', methods=['POST'])
def change_theme():
    THEMES = {
        'purple': {
            'name': 'Purple Theme',
            'stylesheet': url_for('static',filename='scss/purple_theme.css')
        },
        'dark': {
            'name': 'Dark Theme',
            'stylesheet': url_for('static',filename='scss/dark_theme.css')
        },
        # 'orange': {
        #     'name': 'Orange Theme',
        #     'stylesheet': url_for('static',filename='scss/orange_theme.css')
        # },
        'pink': {
            'name': 'Pink Theme',
            'stylesheet': url_for('static',filename='scss/styles.css')
        }
        }
    theme = request.json.get('theme')
    if theme in THEMES:
        session['theme'] = theme
        return jsonify({
            'success': True,
            'stylesheet': THEMES[theme]['stylesheet']
        })
    return jsonify({'success': False}), 400

@blp.route('/version')
def version():
    version = HelperClass.get_version()
    return {"version": version}

@blp.route('/print')
def print():
    session_data = session.get('payload')
    if not session_data:
        return redirect(url_for('mobile.index'))
    else:
        payload = json.loads(session_data)
        
    village_count = TerritoryJoin.get_villages_number_by_panchayat(payload['panchayat_id'],payload['block_id'],payload['district_id'])
    tga = BlockOrCensus.get_tga(payload['panchayat_id'],payload['block_id'],payload['district_id'])
    
    human,is_approved = BlockOrCensus.get_human_data(payload['panchayat_id'],payload['block_id'],payload['district_id'])
    
    livestocks,is_approved = BlockOrCensus.get_livestock_data(payload['panchayat_id'],payload['block_id'],payload['district_id'])
    filtered_livestock = [livestock for livestock in livestocks if livestock['count'] > 0]
    
    crops,is_approved = BlockOrCensus.get_crop_data(payload['panchayat_id'],payload['block_id'],payload['district_id'])
    filtered_crops = [crop for crop in crops if crop['count'] > 0]
    
    industries = BudgetData.get_industry_demand(payload['panchayat_id'],payload['block_id'],payload['district_id'])
    filtered_industries = [industries for industries in industries if industries['count'] > 0]
    
    surface_water,is_approved = BlockOrCensus.get_surface_data(payload['panchayat_id'],payload['block_id'],payload['district_id'])
    filtered_surface_water = [waterbody for waterbody in surface_water if waterbody['count'] > 0]
    # surface_rename = {'whs':'WHS','lakes':'Lakes','ponds':'Ponds','tanks':'Tanks','reservoirs':'Resevoirs','others':'Others'}
    # filtered_surface_water = [{**item, 'category':surface_rename[item['category']]} for item in filtered_surface_water]

    
    groundwater,is_approved = BlockOrCensus.get_ground_data(payload['panchayat_id'],payload['block_id'],payload['district_id']) 
    groundwater_rename = {'extraction':'Extracted Groundwater','extractable':'Extractable Groundwater','stage_of_extraction':'Stage of Extraction','category':'Category'}
    groundwater = [{**item, 'name':groundwater_rename[item['name']]} for item in groundwater]
    
    water_transfer = BudgetData.get_water_transfer(payload['panchayat_id'],payload['block_id'],payload['district_id'])

    runoff,is_approved = BlockOrCensus.get_runoff_data(payload['panchayat_id'],payload['block_id'],payload['district_id'])
    run_off_rename = {'good':'Good Catchment','bad':'Bad Catchment','average':'Average Catchment'}
    runoff = [{**item, 'catchment':run_off_rename[item['catchment']]} for item in runoff]
    
    rainfall,is_approved = BlockOrCensus.get_rainfall_data(payload['panchayat_id'],payload['block_id'],payload['district_id'])
    rainfall_rename = {'Jan':'January','Feb':'February','Mar':'March','Apr':'April','May':'May','Jun':'June','Jul':'July',
                        'Aug':'August','Sep':'September','Oct':'October','Nov':'November','Dec':'December'}
    for item in rainfall:
        month_abbr = item['month'].split('-')[0]
        year = item['month'].split('-')[1]
        full_month_name = rainfall_rename.get(month_abbr, month_abbr)
        item['month'] = f"{full_month_name}-{year}"

    
    demand_side = BlockOrCensus.get_demand_side_data(payload['panchayat_id'],payload['block_id'],payload['district_id'])
    demand_rename = {'Human':'Human Population Consumption','Livestock':'Livestock Population Consumption'
                        ,'Crop':'Crops Consumption','Industry':'Industry Consumption'}
    demand_side = [{**item, 'category':demand_rename[item['category']]} for item in demand_side]
    
    supply_side = BlockOrCensus.get_supply_side_data(payload['panchayat_id'],payload['block_id'],payload['district_id'])
    # supply_rename = {'Surface':'Available Surface Water','Ground':'Ground Water'}
    for item in supply_side:
        if item['category'] == 'Transfer':
            if item['value'] >0:
                item['category'] = 'Water Transfer Inward'
                transfer_indicator = 'inward'
            else:
                transfer_indicator = 'outward'
                item['category'] = 'Water Transfer Outward'
        # else:
        #     item['category'] = supply_side[item['category']]
    
    water_budget = BlockOrCensus.get_water_budget_data(payload['panchayat_id'],payload['block_id'],payload['district_id'])
    water_budget_rename = {'Demand':'Total Demand','Supply':'Total Supply'}
    water_budget = [{**item, 'category':water_budget_rename[item['category']]} for item in water_budget]
    
    return render_template('mobile/print.html',village_count=village_count,tga=round(tga,2),human_data=human,human=json.dumps(human),
                           livestock_data=filtered_livestock,crop_data=filtered_crops,
                           surface_water_data=filtered_surface_water,industry_data=filtered_industries,
                           groundwater_data=groundwater, transfer_data=water_transfer, runoff_data=runoff,rainfall_data=rainfall,transfer_indicator=transfer_indicator,
                           water_budget=water_budget,demand_side=demand_side,supply_side=supply_side,payload=payload)

def get_breadcrumbs(payload):
    """
    Generate breadcrumb navigation based on the current payload.

    Returns:
        list: Breadcrumbs for the current context.
    """
    return [
        {'name': payload['district_short_name'], 'href': '#'},
        {'name': payload['block_name'], 'href': '#'},
        {'name': payload['panchayat_name'], 'href': '#'}
    ]

def get_supply_menu():
    return [
        { "route" : url_for('.home'), "label":"back", "icon":"fa-solid fa-left-long"},
        { "route" : url_for('.surface'), "label":"surface", "icon":"fa-solid fa-water"},
        { "route" : url_for('.ground'), "label":"ground", "icon":"fa-solid fa-arrow-up-from-ground-water"},
        { "route" : url_for('.runoff'), "label":"runoff", "icon":"fa-solid fa-cloud-showers-water"},
        { "route" : url_for('.rainfall'), "label":"rainfall", "icon":"fa-solid fa-cloud-rain"},
    ]

def get_demand_menu():
    return [
        { "route" : url_for('.home'), "label":"back", "icon":"fa-solid fa-left-long"},
        { "route" : url_for('.human'), "label":"human", "icon":"fa-solid fa-people-roof"},
        { "route" : url_for('.livestocks'), "label":"livestock", "icon":"fa-solid fa-paw"},
        { "route" : url_for('.crops'), "label":"crops", "icon":"fa-brands fa-pagelines"},
        { "route" : url_for('.industry'), "label":"industry", "icon":"fa-solid fa-industry"},
    ]

def get_main_menu():
    return [
        { "route" : url_for('.human'), "label":"demand", "icon":"fa-solid fa-chart-line"},
        { "route" : url_for('.index'), "label":"home", "icon":"fa-solid fa-house"},
        { "route" : url_for('.surface'), "label":"supply", "icon":"fa-solid fa-glass-water-droplet"},
    ]