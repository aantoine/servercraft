import os
import urllib
import shutil

from flask import render_template, request, make_response, redirect, url_for, flash, abort, jsonify
from app import app
from auth import auth
from test.models import Jar, get_without_failing, Server
from test.utils import execute, is_name_valid, is_online


@app.route('/login', methods=['GET', 'POST'])
@auth.login('index')
def login(_next=None):
    request.form.get('url', None)
    if request.method == "GET":
        if _next is None:
            return render_template('login.html')
        return render_template('login.html', next=True, url=_next)
    return render_template('login.html', alert=True)


@app.route('/logout')
@auth.logout
def logout():
    flash("Logging out")
    return make_response(redirect(url_for('index')))


@app.route('/config', methods=['GET'])
@auth.login_required
def get_config():
    return render_template('config.html')


@app.route('/config', methods=['POST'])
@auth.login_required
@auth.post_credentials('configPassword')
def post_config():
    resp = make_response(render_template(
        'config.html',
        alert=True))
    return resp


##############################################################################


@app.route('/')
@auth.setup_required('get_config')
@auth.check_logged_in
def index(is_logged_in):
    servers = Server.select()
    status = []
    for _server in servers:
        print _server.name
        status.append(is_online(execute([app.config['SCRIPT'], "status", _server.name])))
    if is_logged_in:
        return render_template('index_auth.html',
                               servers=servers,
                               status=status,
                               server_success=request.args.get('server_success', False))
    return render_template('index.html', servers=servers, status=status)


@app.route('/create/server', methods=['GET'])
@auth.login_required
def create_server():
    return render_template('server_create.html', jars=Jar.select())


@app.route('/create/server', methods=['POST'])
@auth.login_required
def post_server():
    jar = request.form.get('jar', None)
    name = request.form.get('name', None)
    size = request.form.get('size', None, type=int)
    xms = request.form.get('xms', None, type=int)
    xmx = request.form.get('xmx', None, type=int)
    if jar is None or name is None or size is None or xmx is None or xms is None or not is_name_valid(name):
        print "error1"
        abort(400)

    jar = Jar.select().where(Jar.id == jar).get()
    if not jar.downloaded:
        print "error2"
        abort(400)

    if get_without_failing(Server, (Server.name == name)) is not None:
        print "error3"
        abort(400)

    if xms >= xmx:
        print "error4"
        abort(400)
    _server = Server(name=name, jar=jar, java_size=size, xmx=xmx, xms=xms)
    server_path = app.config['SERVERS_FOLDER'] + _server.name

    if os.path.exists(server_path):
        print "error5"
        abort(400)

    os.makedirs(server_path)
    # Copy eula.txt
    shutil.copy(app.config['SERVERS_FOLDER'] + 'eula.txt', server_path + "/eula.txt")

    _server.save()
    return redirect(url_for('index', server_success=True))


@app.route('/jar/download')
@auth.login_required
def jar_download():
    jar = request.args.get('jar', 0, type=int)
    if jar == 0:
        abort(400)
    jar = Jar.select().where(Jar.id == jar).get()
    if not jar.downloaded:
        jar_path = app.config['JARS_FOLDER'] + jar.name
        urllib.urlretrieve(jar.url, jar_path)
        jar.downloaded = True
        jar.path = jar_path
        jar.save()
    return jsonify(result=jar.downloaded)


@app.route('/jar/downloaded')
@auth.login_required
def jar_downloaded():
    jar = request.args.get('jar', 0, type=int)
    if jar == 0:
        abort(400)
    jar = Jar.select().where(Jar.id == jar).get()
    return jsonify(result=jar.downloaded)


@app.route('/command/<_command>/<_server>')
@auth.login_required
def command(_command, _server):
    _server = get_without_failing(Server, (Server.id == _server))
    if _server is None:
        abort(400)
    output = "NULL"
    if _command == "status":
        output = execute([app.config['SCRIPT'], "status", _server.name])
    elif _command == "start":
        output = execute([app.config['SCRIPT'], "start", _server.name])
    elif _command == "stop":
        output = execute([app.config['SCRIPT'], "stop", _server.name])
    return jsonify(output=output)


@app.route('/server/<_server>')
@auth.login_required
def server(_server):
    return render_template('server_view.html', server=_server)


@app.route('/properties/<_server>')
@auth.login_required
def properties(_server):
    return render_template('properties_view.html', server=_server)
