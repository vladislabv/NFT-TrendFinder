import os
import time
import glob
import pickle
from flask import render_template, send_from_directory, request, url_for, jsonify, redirect
from nft_finder import db_client, cache
from nft_finder.dashboard import dashboard_bp
from nft_finder.tasks import get_dashboard_data
from config import MEDIA_FOLDER

openings = 0
@cache.cached(timeout=1000)
@dashboard_bp.route('/config', methods=['GET', 'POST'])
def config_dashboard():

    if request.method == 'GET':
        return render_template('dashboard_start.html')

    return redirect(url_for('dashboard.routes.config_dashboard'))
     

@dashboard_bp.route('/showpage', methods = ['GET'])
def showpage():

    list_of_files = glob.glob(os.getcwd() + '/celery_results/*.dat') # * means all if need specific format then *.csv
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
    for i in range(3):
        try:
            res = send_from_directory(MEDIA_FOLDER, filename, as_attachment=True, cache_timeout = 0)
        except Exception as err:
            print(err)
            pass
    return res

@dashboard_bp.route('/longtask', methods=['POST'])
def longtask():
   task = get_dashboard_data.delay()
   return jsonify({}), 202, {
       'Location': url_for(
           'dashboard.taskstatus',
           task_id=task.id
           )
       }

@dashboard_bp.route('/status/<task_id>')
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

