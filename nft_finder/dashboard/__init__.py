# Import flask and template operators
import logging
from flask import Blueprint

logger = logging.getLogger(__name__)

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

import nft_finder.dashboard.routes


