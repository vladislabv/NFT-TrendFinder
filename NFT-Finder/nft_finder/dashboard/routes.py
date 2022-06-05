import os
import time
import json
import glob
import pickle
from flask import render_template, send_from_directory, request, url_for, jsonify, redirect, flash, send_file
from nft_finder import db_client, cache
from nft_finder.dashboard import dashboard_bp
from nft_finder.tasks import get_dashboard_data, generate_picture
from config import MEDIA_FOLDER, DALLE_FOLDER

openings = 0
@cache.cached(timeout=1000)
@dashboard_bp.route('/config', methods=['GET', 'POST'])
def config_dashboard():
    if request.method == 'GET':
        return render_template('dashboard_start.html', data=json.dumps({}))

    return redirect(url_for('dashboard.routes.config_dashboard'))
     

@dashboard_bp.route('/showpage', methods = ['GET'])
def showpage():

    list_of_files = glob.glob(os.getcwd() + '/celery_results/*.dat')
    latest_file = max(list_of_files, key=os.path.getctime)

    objects = []
    with (open(latest_file, "rb")) as openfile:
        while True:
            try:
                objects.append(pickle.load(openfile))
            except EOFError:
                break
    objects = objects[0]

    return render_template(
        'dashboard.html',
        top_pairs = objects.get('top_pairs'),
        generated_pairs = objects.get('generated_pairs'),
        rich_pairs = objects.get('rich_pairs'),
        rich_images_with_info = objects.get('rich_images_with_info')
        )

@dashboard_bp.route('/uploads/<path:filename>')
def download_file(filename):
    return send_from_directory(MEDIA_FOLDER, filename, as_attachment=True, cache_timeout = 0)

@dashboard_bp.route('/download')
def download_picture():
    list_of_folders = glob.glob(os.path.join(DALLE_FOLDER, 'outputs', '*'))
    latest_folder = max(list_of_folders, key=os.path.getmtime)
    gen_pictures = glob.glob(os.path.join(latest_folder, '*.png'))
    gen_pictures.extend(glob.glob(os.path.join(latest_folder, '*.jpg')))
    gen_pictures.sort(key=os.path.getctime)
    result = gen_pictures[0]
    ext = result.split('.')[-1]
    name = latest_folder.split('\\')[-1]
    return send_file(
        result,
        mimetype = f"image/{ext.lower()}",
        attachment_filename=f"{name}.{ext}", 
        as_attachment=True
        )

@dashboard_bp.route('/combine-selections')
def combine_selections():
    if request.form.get('selected_items'):
        user_choice = request.form.get('selected_items')
        print(user_choice)
    return True

@dashboard_bp.route('/longtask', methods=['POST'])
def longtask():
   num_items = int(request.args.get('num_items'))
   start_date = request.args.get('start_date')
   end_date = request.args.get('end_date')
   task = get_dashboard_data.delay(num_items, start_date, end_date)
   return jsonify({}), 202, {
       'Location': url_for(
           'dashboard.taskstatus',
           task_id=task.id
           )
       }

@dashboard_bp.route('/picture_longtask', methods=['POST'])
def picture_longtask():
    data = request.args.get('data')
    task = generate_picture.delay(data)
    return jsonify({}), 202, {
       'Location': url_for(
           'dashboard.taskstatus',
           task_id=task.id
           )
       }

@dashboard_bp.route('/status/<task_id>', methods=['GET'])
def taskstatus(task_id):
    task = get_dashboard_data.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)

