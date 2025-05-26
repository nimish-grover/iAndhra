from flask import Blueprint, flash, get_flashed_messages, json, jsonify, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user
from app.classes.helper import HelperClass
from app.models.feedback import Feedback
from app.models.states import State
from app.models.territory import TerritoryJoin
from app.models.users import User
from app.classes.block_or_census import BlockOrCensus
import os
from werkzeug.utils import secure_filename

blp = Blueprint("auth","auth")
UPLOAD_FOLDER = os.path.join(os.getcwd(),'app','static','uploads', 'feedback')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}


@blp.route('/register', methods=['POST','GET'])
def register():
    message = get_message()
    if request.method=='POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirmPassword')
        district_id = request.form.get('dd_districts')
        block_id = request.form.get('dd_blocks')
        panchayat_id = request.form.get('dd_panchayats')
        panchayat_arr = [int(item) for item in panchayat_id.split(',')]
        user = User.find_by_username(username.lower())
        if user:
            flash('username already exists!')
            return redirect(url_for('auth.register'))
        
        if password != confirm_password:
            flash('Passwords do not match!')
            return redirect(url_for('auth.register'))

        user = User(username.lower(),password,district_id,block_id,panchayat_arr,False,False)
        user.set_password(password)
        user.save_to_db()

        flash('Registered successfully!')
        return redirect(url_for('auth.login'))
    districts = TerritoryJoin.get_districts()
    return render_template("auth/register_user.html", 
                           flash_message=message, 
                           districts = districts)

@blp.route('/login', methods=['POST','GET'])
def login():
    if request.method=='POST':
        username = request.form.get('username')
        password = request.form.get('password')
        next = request.args.get('next')
        try:        
            user = User.query.filter_by(username=username.lower()).first()
            if user and User.check_password(user, password) and user.isActive:
                login_user(user)
                return redirect(url_for('mobile.index'))
            elif user is None:
                flash('User does not exist!')
            elif not User.check_password(user, password):
                flash('Password is incorrect')
            elif not user.isActive:
                flash('User is not authorized. Please contact Block Coordinator')
        except Exception as e:
            flash('There was an error while connecting to database!')
            print(e)
    message = get_message()
    return render_template('auth/login.html', flash_message = message)

@blp.route('/logout')
def logout():
    logout_user()
    session.clear()
    session['logged_out']=True
    return redirect(url_for('.login'))

@blp.route('/change_password', methods=['POST','GET'])
@login_required
def change_password():
    if request.method=='POST':
        password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        try:
            user = User.query.filter_by(id=current_user.id).first()
            if user and User.check_password(user, password) and user.isActive:
                if new_password == confirm_password:
                    user.set_password(new_password)
                    user.update_db()
                    flash('Password changed successfully! Please login with new password!')
                    return redirect(url_for('auth.logout'))
                else:
                    flash('new and confirm password do not match!')
                    return redirect(url_for('auth.change_password'))
            elif user is None:
                flash('User does not exist!')
            elif not User.check_password(user, password):
                flash('Old password is incorrect')
            elif not user.isActive:
                flash('User is not active. Please contact State Coordinator')
        except Exception as e:
            flash('There was an error while connecting to database!')
            print(e)    
    message = get_message()
    return render_template("auth/change_password.html", flash_message = message)

@blp.route('/forgot_password')
@login_required
def forgot_password():
    return render_template("auth/forgot_password.html")

@blp.route('/reset_password', methods=['POST','GET'])
@login_required
def reset_password():
    if current_user.isAdmin: 
        users = User.get_all()           
        if request.method=='POST':
            try:
                json_data = request.json
                user = User.query.filter_by(id=json_data['id']).first()
                if user and user.isActive:
                    reset_pwd = user.username[:4] + '_123'
                    user.set_password(reset_pwd)
                    user.update_db()
                    flash('Password reset successfully! Please login with new password!')
                    return {'redirect_url' : url_for('auth.approve')}
                elif user is None:
                    flash('User does not exist!')
                elif not user.isActive:
                    flash('User is not active!')
            except Exception as e:
                flash('There was an error connecting to database!')
                print(e)        
        # return render_template("auth/reset_password.html")
    else:
        flash("Only admin can reset password!")
    message = get_message()
    return render_template("auth/reset_password.html",
                           post_url = url_for('.reset_password'),
                           flash_message = message,
                           users=users,
                           user_data=json.dumps(users))
    

@blp.route('/approve', methods=['POST','GET'])
@login_required
def approve():
    if request.method =='POST':
        json_data = request.json
        for item in json_data:
            if item['id']:
                user_object = User.get_by_id(item['id'])
                user_object.isActive = bool(item['isActive'])
                user_object.update_db()
        flash("The user(s) is/are approved!!")
        return jsonify({'redirect_url': url_for('mobile.index')})
    if current_user.isAdmin:
        users = User.get_all()
        # states = State.get_all()
        message = get_message()
        return render_template('auth/approve.html',
                            flash_message = message,
                            users=users,
                            user_data=json.dumps(users),
                            menu= HelperClass.get_admin_menu())
    else: 
        flash('You must be admin to view this page!')
        return redirect(url_for('auth.login'))

@blp.route('/dashboard',methods=['POST','GET'])
@login_required
def dashboard():
    card_data = HelperClass.get_card_data()
    chart_data =HelperClass.get_chart_data()

    return render_template('auth/dashboard.html',
                           card_data = card_data,
                           chart_data = json.dumps(chart_data),
                           flash_message = get_message(),
                           menu= HelperClass.get_admin_menu())

@blp.route('/progress')
@login_required
def progress():
    if current_user.isAdmin:
        progress = HelperClass.get_panchayat_progress()
        status_dummy = [{'category':'Human','id':'human'},
                        {'category':'Livestocks','id':'livestock'},
                        {'category':'Crops','id':'crop'},
                        {'category':'Industry','id':'industry'},
                        {'category':'Surface','id':'surface'},
                        {'category':'Groundwater','id':'groundwater'},
                        {'category':'LULC','id':'lulc'},
                        {'category':'Rainfall','id':'rainfall'},
                        {'category':'Water Transfer','id':'transfer'}]
        return render_template('auth/progress.html',
                            progress=sorted(progress, key=lambda x: x["completed_percentage"], reverse=True),
                            status = status_dummy,
                            menu = HelperClass.get_admin_menu(),
                            progress_data = json.dumps(progress))
    else: 
        flash('You must be admin to view this page!')
        return redirect(url_for('auth.login'))
    
    
@blp.route('/budget',methods=['POST','GET'])
def budget():
    budget_data = HelperClass.get_budget_data()
    
    return render_template('auth/budget.html',budget = budget_data,menu= HelperClass.get_admin_menu()) 

@blp.route('/update_redirect',methods=['POST'])
def update_redirect():
    json_data = request.json
    if json_data:
        session['user_data'] = json_data
        return jsonify({'redirect_url': url_for('auth.user_update')})
    
@blp.route('/user_update',methods=['POST','GET'])
def user_update():
    if request.method == 'POST':
        panchayat_ids = request.form.get('dd_panchayats')
        block_id = session.get('user_data')['block_id']
        district_id = session.get('user_data')['district_id']
        user_id = session.get('user_data')['id']
        result = HelperClass.update_user_panchayat(user_id,panchayat_ids,block_id,district_id)
        if result:
            flash('User updated successfully!')
        else:
            flash('Error updating user!')
        return redirect(url_for('auth.approve'))
    message = get_message()
    user_data = session.get('user_data')
    district = {'id':user_data['district_id'],'name':user_data['district_name']}
    block = {'id':user_data['block_id'],'name':user_data['block_name']}
    isactive = User.check_active(user_data['id'])
    user = {'name':user_data['username'],'id':user_data['id'],'isactive':isactive}
    return render_template('auth/user_update.html',
                           flash_message=message, 
                           block=block,
                           user=user,
                           district=district)

@blp.route('/user_profile',methods=['GET'])
@login_required
def user_profile():
    message = get_message()
    district = {'id':current_user.district_id,'name':HelperClass.get_district_name(current_user.district_id)}
    block = {'id':current_user.block_id,'name':HelperClass.get_block_name(current_user.block_id)}
    panchayat = current_user.panchayat_id
    panchayat_name = HelperClass.get_panchayat_name(current_user.panchayat_id)
    isactive = current_user.isActive
    user = {'name':current_user.username,'id':current_user.id,'isactive':isactive}
    return render_template('auth/profile.html',
                           flash_message=message, 
                           block=block,
                           user=user,
                           district=district,
                           panchayats=panchayat_name)
    

@blp.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        category = request.form.get('category')
        email = request.form.get('email') or None
        message = request.form.get('message')
        if category == 'other':
            category = request.form.get('other_issue')
        

        file = request.files.get('attachment')
        file_path = None

        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)

        new_feedback = Feedback(
            category=category,
            email=email,
            message=message,
            file_path=filename if file_path else None
        )

        new_feedback.save_to_db()

        flash("Thank you! Your feedback has been submitted.")
        return redirect(url_for('auth.feedback'))

    return render_template("auth/feedback.html",email=current_user.username if current_user.is_authenticated else '',)

@blp.route('/view_feedback', methods=['GET'])
def view_feedback():
    if not current_user.isAdmin:
        flash('You must be admin to view this page!')
        return redirect(url_for('auth.login'))
    feedbacks = Feedback.get_all_feedback()
    return render_template("auth/view_feedback.html", feedbacks=feedbacks,menu= HelperClass.get_admin_menu())

@blp.route('/reset_pwd', methods=['POST', 'GET'])
def reset_pwd_no_login():
    if request.method == 'POST':
        username = request.form.get('email')
        user = User.find_by_username(username.lower())
        if user:
            feedback = Feedback('reset_password',user.username, 'Request to reset password', None)
            feedback.save_to_db()
            
            flash('Reset password request submitted successfully!')
            return redirect(url_for('auth.login'))
        else:
            flash('Username entered is wrong !')
        return redirect(url_for('auth.login'))  
    return render_template("auth/reset_pwd_no_login.html")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



def get_message():
    messages = get_flashed_messages()
    # if len(messages) > 0:
    #     message = messages[0]
    # else:
    #     message = ''

    return messages
