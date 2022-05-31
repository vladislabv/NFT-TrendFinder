import asyncio
from flask import render_template, send_from_directory, redirect, url_for
from dashboard import dashboard_bp
from app import cache
from helpers.add_extensions import get_or_create_eventloop
from dashboard.mongo_queries import AGG_PIPELINES_DICT
from dashboard.prepare_data import prepare_data
from config import MEDIA_FOLDER

@dashboard_bp.route('/config', methods=['GET', 'POST'])
def config_dashboard():
    return render_template('auth/test.html')


@dashboard_bp.route('/uploads/<path:filename>')
def download_file(filename):
    return send_from_directory(MEDIA_FOLDER, filename, as_attachment=True)

count_showpage = 0
@cache.cached(timeout=100000)
@dashboard_bp.route('/showpage')
async def showpage():
    global count_showpage
    if not count_showpage:
        #from .mongo_queries import pair_aggregation, value_aggregation, key_aggregation, rich_items
        ## get data from the mongodb tables
        #rich_items_data = list(NftItem._get_collection().aggregate(rich_items))
        #top_pairs_data = list(ItemAttribute._get_collection().aggregate(pair_aggregation))
        #top_values = list(ItemAttribute._get_collection().aggregate(value_aggregation))
        #top_keys = list(ItemAttribute._get_collection().aggregate(key_aggregation))
        loop = get_or_create_eventloop()
        asyncio.set_event_loop(loop)
        dashboard_data = loop.run_until_complete(
            asyncio.gather(*[
                execute_agg_pipeline(
                    db_async,
                    collection = AGG_PIPELINES_DICT[i][0],
                    agg_pipeline = AGG_PIPELINES_DICT[i][1],
                    pipeline_name = i
                    ) for i in AGG_PIPELINES_DICT
                ])
            )
        
        dashboard_data = prepare_data(dashboard_data)
        count_showpage += 1
        cache.add("dashboard_showpage_top_pairs",dashboard_data['top_pairs'])
        cache.add("dashboard_showpage_generated_pairs", dashboard_data['generated_pairs'])
        cache.add("dashboard_showpage_rich_pairs", dashboard_data['rich_pairs'])
        cache.add("dashboard_showpage_rich_images_with_info", dashboard_data['rich_images_with_info'])
    try:
        return render_template(
            'analysis.html', 
            top_pairs = cache.get("dashboard_showpage_top_pairs"), 
            generated_pairs = cache.get("dashboard_showpage_generated_pairs"),
            rich_pairs = cache.get("dashboard_showpage_rich_pairs"),
            rich_images_with_info = cache.get("dashboard_showpage_rich_images_with_info")
            )
    except TypeError as err:
        print("The cache is expired, fetching the data again...")
        count_showpage = 0
        redirect(url_for('dashboard.showpage'))