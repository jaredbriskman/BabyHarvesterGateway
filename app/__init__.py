from flask import Flask, request, Response
from flask_mqtt import Mqtt, MQTT_LOG_ERR
from flask_migrate import Migrate
from flask_sslify import SSLify
from functools import wraps
from app.models import *
import os
import random

app = Flask(__name__)

# Debug
if os.environ["FLASK_ENV"] is 'prod':
    app.config['DEBUG'] = False
    sslify = SSLify(app, age=1000)
else:
    app.config['DEBUG'] = True

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

def check_auth(name, password, realm):
    """Validates credentials against db"""
    if realm is "changeToken":
        return (password == os.environ["APP_SECRET"])
    else:
        auth_check = User.query.filter_by(name=name,password=password).first()
        return (auth_check is not None)

def authenticate(realm="Login Required"):
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="{}"'.format(realm)})

def requires_auth(realm="Login Required"):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            #if realm is None:
            #    realm = "Login Required" 
            auth = request.authorization
            if not auth or not check_auth(auth.username, auth.password, realm):
                return authenticate(realm)
            return f(*args, **kwargs)
        return decorated
    return decorator

def pass_text(channel=None):
    """Generic method to pass a payload to a device over MQTT"""
    device = request.authorization.username
    channel = "{}/{}".format(device, channel)
    data = request.get_json()
    mqtt.publish(channel, data['message'])
    return 'Message {} published to topic {}'.format(data['message'], channel)
    

@mqtt.on_log()
def handle_logging(client, userdata, level, buf):
    if level == MQTT_LOG_ERR:
        print('MQTT Error: {}'.format(buf))

@app.route('/')
def index():
    return 'Welcome to the Baby Harvester Gateway.'

@app.route('/changetoken')
@requires_auth(realm="changeToken")
def change_token():
    device = request.authorization.username
    u = User.query.filter_by(name=device).first()
    if u is None: # New Device
        u = User(name=device, password=str(random.randint(0, 2 ** 10)))
    else: # Existing Device
        u.password=str(random.randint(0, 2 ** 10))
    print("changing token", u)
    db.session.add(u)
    db.session.commit()
    mqtt.publish("{}/print/text".format(device),"{}".format(u.password))
    return "Token changed"

# These are rather boilerplate, but allow for endpoint specific configuration
@app.route('/display/text', methods=['GET', 'POST'])
@requires_auth()
def display_text():
    return pass_text(channel="display/text")

@app.route('/display/url', methods=['GET', 'POST'])
@requires_auth()
def display_url():
    return pass_text(channel="display/url")

@app.route('/print/text', methods=['GET', 'POST'])
@requires_auth()
def print_text():
    return pass_text(channel="print/text")

@app.route('/light/run', methods=['GET', 'POST'])
@requires_auth()
def light_run():
    """Turn on the light for a specified amount of time, in seconds"""
    return pass_text(channel="light/run")

