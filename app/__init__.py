from flask import Flask
from flask_mqtt import Mqtt

app.config['MQTT_BROKER_URL'] = 'broker.hivemq.com'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = ''
app.config['MQTT_PASSWORD'] = ''
app.config['MQTT_KEEPALIVE'] = 5
app.config['MQTT_TLS_ENABLED'] = False

app = Flask(__name__)
mqtt = Mqtt(app)

@app.route('/')
def index():
    return 'Welcome to the Baby Harvester Gateway.'
