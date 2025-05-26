from flask import Blueprint, render_template, request, redirect, url_for, flash

from app.classes.helper import HelperClass
import os 

ERROR_LOG_DIR = 'logs'

blp = Blueprint('developer', __name__, url_prefix='/dev')

@blp.route('/version')
def version():
    version = HelperClass.get_version()
    return {"version": version}

@blp.route('/errors', methods=['GET', 'POST'])
def error_logs():
    if not os.path.exists(ERROR_LOG_DIR):
        os.makedirs(ERROR_LOG_DIR)

    log_files = [f for f in os.listdir(ERROR_LOG_DIR) if os.path.isfile(os.path.join(ERROR_LOG_DIR, f))]
    selected_file = request.args.get('file')
    file_content = ""

    if selected_file and selected_file in log_files:
        with open(os.path.join(ERROR_LOG_DIR, selected_file), 'r') as f:
            file_content = f.read()

    return render_template('developer/error.html', files=log_files, content=file_content, selected_file=selected_file)


@blp.route('/error_delete', methods=['POST'])
def delete_log_file():
    filename = request.form.get('filename')
    if filename == "all":
        for f in os.listdir(ERROR_LOG_DIR):
            os.remove(os.path.join(ERROR_LOG_DIR, f))
        flash("All log files deleted.", "success")
    else:
        file_path = os.path.join(ERROR_LOG_DIR, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            flash(f"File {filename} deleted.", "success")
    return redirect(url_for('.error_logs'))