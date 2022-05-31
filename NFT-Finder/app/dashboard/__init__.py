# Import flask and template operators
import os
import sys
import logging
from flask import Blueprint
from pymongo import mongo_client
BASE_deep = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE_deep)
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)
from config import MONGODB_CONNECTION_STRING, MONGODB_DB

logger = logging.getLogger(__name__)

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@celery.task()
def get_dashboard_data():
    result = []
    with mongo_client(MONGODB_CONNECTION_STRING) as client:
        db = client[MONGODB_DB]
        for pipeline_name in AGG_PIPELINES_DICT:
            collection = AGG_PIPELINES_DICT[pipeline_name][0]
            pipeline = AGG_PIPELINES_DICT[pipeline_name][1]
            pip_result_raw = db.collection.aggregate(pipeline)
            pip_result = prepare_data
            result.append((pip_result, pipeline_name))
            pprint(pip_result)
    return result


import routes

#@dashboard_bp.route('/longtask', methods=['POST'])
#def longtask():
#    nb_days = 1
#    output_limit = 1000
#    task = fetch_item_info.apply_async(args=[nb_days, output_limit])
#    return jsonify({}), 202, {
#        'Location': url_for(
#            'dashboard.taskstatus',
#            task_id=task.id
#            )
#        }

# @dashboard_bp.route('/status/<task_id>')
# def taskstatus(task_id):
#     task = fetch_item_info.AsyncResult(task_id)
#     if task.state == 'PENDING':
#         response = {
#             'state': task.state,
#             'current': 0,
#             'total': 1,
#             'status': 'Pending...'
#         }
#     elif task.state != 'FAILURE':
#         response = {
#             'state': task.state,
#             'current': task.info.get('current', 0),
#             'total': task.info.get('total', 1),
#             'status': task.info.get('status', '')
#         }
#         if 'result' in task.info:
#             response['result'] = task.info['result']
#     else:
#         # something went wrong in the background job
#         response = {
#             'state': task.state,
#             'current': 1,
#             'total': 1,
#             'status': str(task.info),  # this is the exception raised
#         }
#     return jsonify(response)

# @dashboard_bp.route('/get-dashboard-data')
# async def get_dashboard_data():
#     app = make_app()
#     client = tornado.ioloop.IOLoop.current().run_sync(get_server_info)
#     db = client['nft-finder']
#     logger.info(f"Database accessed: {db}")

#     loop = get_or_create_eventloop()
#     asyncio.set_event_loop(loop)

#     result = loop.run_until_complete(
#         asyncio.gather(*[
#             execute_agg_pipeline(
#                 db,
#                 collection = AGG_PIPELINES_DICT[i][0],
#                 agg_pipeline = AGG_PIPELINES_DICT[i][1],
#                 pipeline_name = i
#                 ) for i in AGG_PIPELINES_DICT
#             ])
#         )
    
#     result = prepare_data(result)

#     return result



