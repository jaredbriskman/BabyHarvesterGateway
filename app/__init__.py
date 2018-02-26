from flask import Flask, request, Response
from flask_mqtt import Mqtt
from flask_migrate import Migrate
from flask_sslify import SSLify
from functools import wraps
from app.models import *
import os

app = Flask(__name__)

# Debug
if os.environ["FLASK_ENV"] is 'DEV':
    app.config['DEBUG'] = True
else:
    app.config['DEBUG'] = False

# MQTT
app.config['MQTT_BROKER_URL'] = os.environ["MQTT_BROKER_URL"]
app.config['MQTT_BROKER_PORT'] = int(os.environ["MQTT_BROKER_PORT"])
app.config['MQTT_USERNAME'] = os.environ["MQTT_USERNAME"]
app.config['MQTT_PASSWORD'] = os.environ["MQTT_PASSWORD"]
app.config['MQTT_KEEPALIVE'] = 5
app.config['MQTT_TLS_ENABLED'] = False
mqtt = Mqtt(app)

# DB
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Handles deprecation warning
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["DATABASE_URL"]
db.init_app(app)
migrate = Migrate(app, db)

# SSL
sslify = SSLify(app, age=300)

def check_auth(name, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    auth_check = User.query.filter_by(name=name,password=password).first()
    return (auth_check is not None)

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def index():
    return 'Welcome to the Baby Harvester Gateway.'

@app.route('/secret')
@requires_auth
def secret_page():
    return "It's a secret."
