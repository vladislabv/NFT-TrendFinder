# Import flask and template operators
from .tasks import fetch_item_info, fetch_user_info
from flask import Blueprint, request, redirect, render_template, url_for, jsonify

#from app import celery
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/config', methods=['GET', 'POST'])
def config_dashboard():
    is_run = False
    current = None
    total = None
    if request.method == 'GET':
      return render_template('auth/config.html')
    else:
        if request.form.get("ext_items"):
            if request.form.get("nb_days"):
                task_item = fetch_item_info.delay(nb_days = request.form.get('nb_days'))
                is_run = True
                current = task_item
                
        if request.form.get("ext_users"):
            if task_item.get('status', '') == 'FINISHED':
                task_user = fetch_user_info.delay()
             
        if task_user.get('status', '') == 'FINISHED':
            render_template('auth/config.html', current=current, total=total)
    return render_template('auth/config.html', progress_run = is_run)

@dashboard_bp.route('/showpage')
def showpage():
    return render_template('analysis.html')



