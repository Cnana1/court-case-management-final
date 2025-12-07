from .auth_routes import auth_bp
from .schedule_routes import schedule_bp
from .case_routes import case_bp
from .courtdate_routes import courtdate_bp
from .request_routes import request_bp
from .reschedule_routes import reschedule_bp
from .admin_routes import admin_bp 
from .users import bp_users


blueprints = [
    auth_bp,
    schedule_bp,
    case_bp,
    courtdate_bp,
    request_bp,
    reschedule_bp,
    admin_bp,
    bp_users
]
