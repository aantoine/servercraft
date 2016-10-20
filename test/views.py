import os
import urllib
import shutil

from flask import request, make_response, redirect, url_for, flash, abort, jsonify
from app import app
from auth import auth
from test.models import Jar, get_without_failing, Server
from test.utils import execute, is_name_valid, is_online, render_template, redirect


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
        status.append(is_online(execute([app.config['SCRIPT'], "status", _server.name])))
    if is_logged_in:
        return render_template('index_auth.html',
                               servers=servers,
                               status=status)
    return render_template('index.html', servers=servers, status=status)


@app.route('/create/server', methods=['GET'])
@auth.login_required
def create_server():
    return render_template('server_create.html', jars=Jar.select())


@app.route('/delete', methods=['POST'])
@auth.login_required
def server_delete():
    server_id = request.form.get('server_id', None)
    _server = get_without_failing(Server, (Server.id == server_id))
    if _server is None:
        abort(400)
    shutil.rmtree(app.config['SERVERS_FOLDER'] + _server.name)
    _server.delete_instance()
    return redirect(url_for('index'), success="Server has been deleted.")


@app.route('/create/server', methods=['POST'])
@auth.login_required
def post_server():
    jar = request.form.get('jar', None)
    name = request.form.get('name', None)
    size = request.form.get('size', None, type=int)
    xms = request.form.get('xms', None, type=int)
    xmx = request.form.get('xmx', None, type=int)
    if jar is None or name is None or size is None or xmx is None\
            or xms is None or not is_name_valid(name):
        return redirect(url_for('create_server'), error="All fields must be filled in.")

    jar = Jar.select().where(Jar.id == jar).get()
    if not jar.downloaded:
        print "error2"
        abort(400)

    if get_without_failing(Server, (Server.name == name)) is not None:
        return redirect(url_for('create_server'), error="Server name must be unique.")

    if xms >= xmx:
        return redirect(url_for('create_server'), error="XMX must be higher than XMS.")
    _server = Server(name=name, jar=jar, java_size=size, xmx=xmx, xms=xms)
    server_path = app.config['SERVERS_FOLDER'] + _server.name

    if os.path.exists(server_path):
        print "error5"
        abort(400)

    os.makedirs(server_path)
    # Copy eula.txt
    shutil.copy(app.config['SERVERS_FOLDER'] + 'eula.txt', server_path + "/eula.txt")

    _server.save()
    return redirect(url_for('index'), success="Server has been created.")


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
        server_path = app.config['SERVERS_FOLDER'] + _server.name
        java_path = app.config['JARS_FOLDER'] + _server.jar.path
        jar_xmx = str(_server.xmx * _server.java_size)
        jar_xms = str(_server.xms * _server.java_size)
        sleep_time = str(10)

        output = execute(
            [app.config['SCRIPT'], "start", server_path, _server.name, java_path, jar_xmx, jar_xms, sleep_time])

    elif _command == "stop":
        output = execute([app.config['SCRIPT'], "stop", _server.name])
    return jsonify(output=output[0:-1])


@app.route('/server/update/jar', methods=['POST'])
@auth.login_required
def server_general_jar():
    server_id = request.form.get('server_id', 0)
    if server_id == 0:
        abort(400)
    _server = get_without_failing(Server, (Server.id == server_id))
    if _server is None:
        abort(400)
    _id = request.form.get('jar', None, type=int)
    xmx = request.form.get('xmx', None, type=int)
    xms = request.form.get('xms', None, type=int)
    size = request.form.get('size', None, type=int)

    if _id is None or xmx is None or xms is None or size is None:
        abort(400)

    if xms >= xmx:
        return redirect(url_for('server', _server=server_id),
                        error="XMX must be higher than XMS.")

    if _id == _server.jar.id and xmx == _server.xmx \
            and xms == _server.xms and size == _server.java_size:
        return redirect(url_for('server', _server=server_id))

    if not _id == _server.jar.id:
        _jar = get_without_failing(Jar, (Jar.id == _id))
        _server.jar = _jar
    if not xmx == _server.xmx:
        _server.xmx = xmx
    if not xms == _server.xms:
        _server.xms = xms
    if not size == _server.java_size:
        _server.java_size = size
    _server.save()

    return redirect(url_for('server', _server=server_id),
                    success="Jar Server properties have been saved.")


@app.route('/server/update/general', methods=['POST'])
@auth.login_required
def server_general_update():
    server_id = request.form.get('server_id', 0)
    if server_id == 0:
        abort(400)
    _server = get_without_failing(Server, (Server.id == server_id))
    if _server is None:
        abort(400)
    new_name = request.form.get('name', None)
    if _server.name == new_name:
        return redirect(url_for('server', _server=server_id))

    if get_without_failing(Server, (Server.name == new_name)) is not None:
        return redirect(url_for('server', _server=server_id), error="Server name must be unique.")

    server_path = app.config['SERVERS_FOLDER'] + _server.name
    new_server_path = app.config['SERVERS_FOLDER'] + new_name

    _server.name = new_name
    _server.save()

    os.rename(server_path, new_server_path)
    return redirect(url_for('server', _server=server_id),
                    success="General Server properties have been saved.")


@app.route('/server/<_server>')
@auth.login_required
def server(_server):
    _server = get_without_failing(Server, (Server.id == _server))
    status = is_online(execute([app.config['SCRIPT'], "status", _server.name]))
    if _server is None:
        abort(400)
    return render_template('server_view.html',
                           server=_server,
                           jars=Jar.select(),
                           status_online=status)


@app.route('/properties/<_server>')
@auth.login_required
def properties(_server):
    _server = get_without_failing(Server, (Server.id == _server))
    if _server is None:
        abort(400)
    return render_template('properties_view.html', server=_server)
