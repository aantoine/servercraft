import os

from flask import Flask

app = Flask(__name__)

app.config.from_object(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

app.config.update(dict(
    SECRET_KEY='development key',
    JARS_FOLDER=os.path.join(APP_ROOT, 'static/media/jars/'),
    SCRIPTS_FOLDER=os.path.join(APP_ROOT, 'static/media/scripts/'),
    SCRIPT="./script.sh",
    SERVERS_FOLDER=os.path.join(APP_ROOT, 'static/media/servers/')
))
