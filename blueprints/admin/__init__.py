from flask import Blueprint

admin_bp = Blueprint(
    'admin',
    __name__,
    url_prefix='/admin'
)

from . import dashboard
from . import users
from . import temples
from . import reviews
from . import contacts
from . import announcements
from . import accommodations
from . import travel_agents
from . import travel_packages