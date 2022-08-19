from flask import Blueprint
from .routes import get_users, get_shops

testing = Blueprint('testing', __name__)

testing.add_url_rule('/testing/get_users', 'test_get_users', get_users, methods=['GET'])