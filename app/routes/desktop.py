from flask import Blueprint, flash, get_flashed_messages, json, jsonify, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required

from app.classes.block_data import BlockData
from app.classes.budget_data import BudgetData
from app.classes.helper import HelperClass
from app.models import BlockTerritory
from app.models.block_pop import BlockPop


blp = Blueprint('desktop','desktop')

@blp.route('/status')
def status():
    session_data = session.get('payload')
    if not session_data:
        return redirect(url_for('mobile.index'))
    else:
        payload = json.loads(session_data)
    progress_status = BlockData.get_progress_status(panchayat_id=payload['panchayat_id'],
                                            block_id=payload['block_id'], 
                                            district_id=payload['district_id'])
    message = get_message()
    return render_template('desktop/home.html',
                           progress = progress_status,
                           flash_message = get_message(),
                           breadcrumbs=HelperClass.get_breadcrumbs(payload),
                           menu= HelperClass.get_main_menu())


@blp.route('/human', methods=['POST','GET'])
@login_required
def human():
    if request.method=='POST':
        json_data = request.json
        BlockData.update_human(json_data, current_user.id)
        flash('Population Data is Validated/Updated')
        return jsonify({'redirect_url': url_for('.status')})
    session_data = session.get('payload')
    if not session_data:
        return redirect(url_for('mobile.index'))
    else:
        payload = json.loads(session_data)
    human = BlockData.get_human_consumption(panchayat_id=payload['panchayat_id'],
                                            block_id=payload['block_id'], 
                                            district_id=payload['district_id'],
                                            user_id=current_user.id)
    if human:
        
        is_approved = (
            all(row['is_approved'] for row in human if row['is_approved'] is not None) 
            and any(row['is_approved'] is not None for row in human)
        )
    else:
        human,is_approved = BlockData.get_dummy_human(panchayat_id=payload['panchayat_id'],
                                            block_id=payload['block_id'], 
                                            district_id=payload['district_id'])
        
    return render_template('desktop/demand/human.html', 
                           human=human, 
                           human_data=json.dumps(human), 
                           is_approved=is_approved,
                           breadcrumbs=HelperClass.get_breadcrumbs(payload),
                           menu= HelperClass.get_demand_menu())

@blp.route('/livestocks', methods=['POST','GET'])
@login_required
def livestocks():
    if request.method=='POST':
        json_data = request.json
        BlockData.update_livestock(json_data, current_user.id)
        flash('Livestock Data is Validated/Updated')
        return jsonify({'redirect_url': url_for('.status')})
    session_data = session.get('payload')
    if not session_data:
        return redirect(url_for('mobile.index'))
    else:
        payload = json.loads(session_data)
    livestocks = BlockData.get_livestock_consumption(panchayat_id=payload['panchayat_id'],
                                            block_id=payload['block_id'], 
                                            district_id=payload['district_id'],
                                            user_id=current_user.id)
    if livestocks:
        is_approved = (
            all(row['is_approved'] for row in livestocks if row['is_approved'] is not None) 
            and any(row['is_approved'] is not None for row in livestocks)
        )
    else:
        livestocks,is_approved = BlockData.get_dummy_livestock(panchayat_id=payload['panchayat_id'],
                                            block_id=payload['block_id'], 
                                            district_id=payload['district_id'])

    return render_template('desktop/demand/livestock.html', 
                           livestock=livestocks, 
                           livestock_data=json.dumps(livestocks), 
                           is_approved=is_approved,
                           breadcrumbs=HelperClass.get_breadcrumbs(payload),
                           menu= HelperClass.get_demand_menu())

@blp.route('/crops', methods=['POST','GET'])
@login_required
def crops():
    if request.method=='POST':
        json_data = request.json
        BlockData.update_crops(json_data, current_user.id)
        flash('Crops Data is Validated/Updated')
        return jsonify({'redirect_url': url_for('.status')})
    session_data = session.get('payload')
    if not session_data:
        return redirect(url_for('mobile.index'))
    else:
        payload = json.loads(session_data)
    crops = BlockData.get_crops_consumption(panchayat_id = payload['panchayat_id'],
                                            block_id=payload['block_id'], 
                                            district_id=payload['district_id'], 
                                            user_id=current_user.id)
    if crops:
        is_approved = (
            all(row['is_approved'] for row in crops if row['is_approved'] is not None) 
            and any(row['is_approved'] is not None for row in crops)
        )
    else:
        crops,is_approved = BlockData.get_dummy_crops(panchayat_id = payload['panchayat_id'],
                                            block_id=payload['block_id'], 
                                            district_id=payload['district_id'])
        
    return render_template('desktop/demand/crops.html', 
                           crops=crops, 
                           crops_data=json.dumps(crops), 
                           is_approved=is_approved,
                           breadcrumbs=HelperClass.get_breadcrumbs(payload),
                           menu= HelperClass.get_demand_menu())

@blp.route('/industries', methods=['POST','GET'])
@login_required
def industries():
    if request.method=='POST':
        json_data = request.json
        BlockData.update_industries(json_data, current_user.id)
        flash('Industries Data is Validated/Updated')
        return jsonify({'redirect_url': url_for('.status')})
    session_data = session.get('payload')
    if not session_data:
        return redirect(url_for('mobile.index'))
    else:
        payload = json.loads(session_data)
    industries = BlockData.get_block_industries(panchayat_id = payload['panchayat_id'],
                                            block_id=payload['block_id'], 
                                            district_id=payload['district_id'], 
                                            user_id=current_user.id)
    if industries:
        is_approved = (
            all(row['is_approved'] for row in industries if row['is_approved'] is not None) 
            and any(row['is_approved'] is not None for row in industries)
        )
    else:
        industries,is_approved = BlockData.get_dummy_industries(panchayat_id = payload['panchayat_id'],
                                            block_id=payload['block_id'], 
                                            district_id=payload['district_id'])
        
    return render_template('desktop/demand/industry.html', 
                           industries=industries, 
                           industry_data=json.dumps(industries), 
                           is_approved=is_approved,
                           breadcrumbs=HelperClass.get_breadcrumbs(payload),
                           menu= HelperClass.get_demand_menu())

@blp.route('/surface', methods=['POST','GET'])
def surface():
    session_data = session.get('payload')
    if not session_data:
        return redirect(url_for('mobile.index'))
    else:
        payload = json.loads(session_data)
    if request.method=='POST':
        json_data = request.json
        BlockData.update_surface(json_data, current_user.id)
        flash('Surface Water Data is Validated/Updated')
        return jsonify({'redirect_url': url_for('.status')})    
    surface_supply = BlockData.get_surface_supply(panchayat_id = payload['panchayat_id'],
                                            block_id=payload['block_id'], 
                                            district_id=payload['district_id'], 
                                            user_id=current_user.id)
    if surface_supply:
        is_approved = (
            all(row['is_approved'] for row in surface_supply if row['is_approved'] is not None) 
            and any(row['is_approved'] is not None for row in surface_supply)
        )
    else:
        surface_supply,is_approved = BlockData.get_dummy_surface(panchayat_id = payload['panchayat_id'],
                                            block_id=payload['block_id'], 
                                            district_id=payload['district_id'])
        
    return render_template('desktop/supply/surface.html',
                        waterbodies = surface_supply,
                        waterbody_data = json.dumps(surface_supply),
                        is_approved = is_approved,
                        breadcrumbs=HelperClass.get_breadcrumbs(payload),
                        menu= HelperClass.get_supply_menu())

@blp.route('/rainfall', methods=['POST', 'GET'])
def rainfall():
    if request.method=='POST':
        json_data = request.json
        BlockData.update_rainfall(json_data, current_user.id)
        flash('Rainfall Data is Validated/Updated')
        return jsonify({'redirect_url': url_for('.status')})
    session_data = session.get('payload')
    if not session_data:
        return redirect(url_for('mobile.index'))
    else:
        payload = json.loads(session_data)
    rainfall = BlockData.get_rainfall_data(panchayat_id = payload['panchayat_id'],
                                            block_id=payload['block_id'], 
                                            district_id=payload['district_id'], 
                                            user_id=current_user.id)
    if len(rainfall) == 12:
        is_approved = (
            all(row['is_approved'] for row in rainfall if row['is_approved'] is not None) 
            and any(row['is_approved'] is not None for row in rainfall)
        )
        
    return render_template('desktop/supply/rainfall.html', 
                            rainfall=rainfall, 
                            rainfall_data=json.dumps(rainfall), 
                            is_approved=is_approved,
                            breadcrumbs=HelperClass.get_breadcrumbs(payload),
                            menu= HelperClass.get_supply_menu())

@blp.route('/lulc', methods=['POST', 'GET'])
def lulc():
    if request.method=='POST':
        json_data = request.json
        BlockData.update_lulc(json_data, current_user.id)
        flash('LULC Data is Validated/Updated')
        return jsonify({'redirect_url': url_for('.status')})
    session_data = session.get('payload')
    if not session_data:
        return redirect(url_for('mobile.index'))
    else:
        payload = json.loads(session_data)
    lulc = BlockData.get_lulc_supply(panchayat_id = payload['panchayat_id'],
                                            block_id=payload['block_id'], 
                                            district_id=payload['district_id'], 
                                            user_id=current_user.id)
    if lulc:
        is_approved = (
            all(row['is_approved'] for row in lulc if row['is_approved'] is not None) 
            and any(row['is_approved'] is not None for row in lulc)
        )
    else:
        lulc,is_approved = BlockData.get_dummy_lulc(panchayat_id = payload['panchayat_id'],
                                            block_id=payload['block_id'], 
                                            district_id=payload['district_id'])
        
    return render_template('desktop/supply/lulc.html', 
                        lulc=lulc, 
                        lulc_data=json.dumps(lulc), 
                        is_approved=is_approved,
                        breadcrumbs=HelperClass.get_breadcrumbs(payload),
                        menu= HelperClass.get_supply_menu())

@blp.route('/ground', methods=['POST','GET'])
def ground():
    if request.method=='POST':
        json_data = request.json
        BlockData.update_ground(json_data, current_user.id)
        flash('Ground water Data is Validated/Updated')
        return jsonify({'redirect_url': url_for('.status')})
    session_data = session.get('payload')
    if not session_data:
        return redirect(url_for('mobile.index'))
    else:
        payload = json.loads(session_data)
    ground_supply = BlockData.get_groundwater_supply(panchayat_id = payload['panchayat_id'],
                                            block_id=payload['block_id'], 
                                            district_id=payload['district_id'], 
                                            user_id=current_user.id)
    if ground_supply:
        is_approved = (
            all(row['is_approved'] for row in ground_supply if row['is_approved'] is not None) 
            and any(row['is_approved'] is not None for row in ground_supply)
        )
    else:
        ground_supply,is_approved= BlockData.get_dummy_groundwater(panchayat_id = payload['panchayat_id'],
                                            block_id=payload['block_id'], 
                                            district_id=payload['district_id'])

    return render_template('desktop/supply/ground.html',
                           ground_supply = ground_supply,
                           groundwater_data = json.dumps(ground_supply),
                           is_approved = is_approved,
                           breadcrumbs=HelperClass.get_breadcrumbs(payload),
                           menu= HelperClass.get_supply_menu())

@blp.route('/transfer', methods=["POST",'GET'])
def transfer():
    is_approved=False
    if request.method=='POST':
        json_data = request.json
        BlockData.update_water_transfer(json_data, current_user.id)
        flash('Water Transfer Data is Validated/Updated')
        return jsonify({'redirect_url': url_for('.status')})
    session_data = session.get('payload')
    if not session_data:
        return redirect(url_for('mobile.index'))
    else:
        payload = json.loads(session_data)
    transfer_data = BlockData.get_water_transfer(panchayat_id = payload['panchayat_id'],
                                            block_id=payload['block_id'], 
                                            district_id=payload['district_id'], 
                                            user_id=current_user.id)
    
    is_approved = (
        all(row['is_approved'] for row in transfer_data if row['is_approved'] is not None) 
        and any(row['is_approved'] is not None for row in transfer_data)
    )
    
    return render_template('desktop/transfer.html',
                           water_transfer = transfer_data,
                           transfer_data=json.dumps(transfer_data),
                           is_approved = is_approved,
                           breadcrumbs=HelperClass.get_breadcrumbs(payload),
                           menu= HelperClass.get_main_menu())



def get_message():
    messages = get_flashed_messages()
    if len(messages) > 0:
        message = messages[0]
    else:
        message = ''

    return message