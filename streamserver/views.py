#LIBS
from flask import g, request, session,url_for,flash, render_template, send_from_directory, abort, redirect ,jsonify
from functools import wraps
import os, logging, hashlib

#MODULES
from streamserver import app, mediascanner, tagreader

#Logging
logging.basicConfig(format='%(filename)-20s:%(lineno)-5s %(levelname)-8s [%(asctime)s]  %(message)s',
                    level=app.Config.LOG_LEVEL)  #, filename ='streamserver.log'
Log = logging.getLogger(__name__)

#Navigation menu
Navigation = [
    {'caption': 'Library', 'link': 'library'},
    {'caption': 'Folders', 'link': 'folders'},
    {'caption': 'Settings', 'link': 'settings'}
]


def get_nav():
    #res = []
    # for d in Navigation:
    #     dtemp = d.copy()
    #     if dtemp['href'] == request.path:
    #         dtemp['active'] = True
    #     res.append(dtemp)
    return Navigation
###################################
##          useful functions     ##
###################################
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login', next=request.url))
        if session['logged_in']==False:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def try_login(user,pw):
    salt="some salt"
    pwhash = hashlib.sha512(pw.encode('utf-8') + salt.encode('utf-8')).hexdigest()
    res=app.Sqlite3DB.query_db('select 1 from users where username=(?) and passwordhash=(?)',(user,pwhash),one=True)
    if res:
        session['logged_in'] = True
        session['username'] = user
        return True
    else:
        return False
###################################
##           Main views          ##
###################################
@app.route('/')
@login_required
def view_index():

    range = app.Sqlite3DB.get_range(1, 25)
    res = []
    for item in range:
        res.append({'id':item['id'], 'name':item['filename'], 'size':item['size'],'href':'getmedia/' + str(item['id']) + item['format']})
    user=session['username']
    return render_template('random.html', Navigation=get_nav(), Data=res,username=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if try_login(request.form['username'] ,request.form['password'])!=True:
            error = 'Invalid credentials'
        else:
            flash('You were logged in')
            return redirect(url_for('view_index'))
    return render_template('login.html', error=error)

@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    session.pop('username',None)
    flash('You were logged out')
    return redirect(url_for('view_index'))

@app.route('/library')
@login_required
def view_library():
    return render_template('library.html', Navigation=get_nav())

#####################################
##      JSON requests              ##
#####################################
@app.route('/_folder/<id>')
@login_required
def get_dir(id):
    folders=app.Sqlite3DB.query_db('select id, directory from directories where parentid=(?)',(id,))
    files=app.Sqlite3DB.query_db('select * from mediafiles where parentid=(?)',(id,))
    return jsonify(data={'folders':folders,'files':files})

@app.route('/_artist/<id>')
@login_required
def get_artists(id):
    res=[]
    if id=='0':
        res=app.Sqlite3DB.query_db("select id, artist as name from artists")
    else:
        res=app.Sqlite3DB.query_db("select id, album as name from albums where artistid="+id)
    return jsonify(data=res)

@app.route('/_album/<id>')
@login_required
def get_albums(id):
    res=[]
    if id=='0':
        res=app.Sqlite3DB.query_db("select id, album as name from albums")
    else:
        res=app.Sqlite3DB.query_db("select * from mediafiles where albumid="+id)
    return jsonify(data=res)

@app.route('/_genre/<id>')
@login_required
def get_genres(id):
    res=[]
    if id=='0':
        res=app.Sqlite3DB.query_db("select id, genre as name from genres")
    else:
        res=app.Sqlite3DB.query_db("select * from mediafiles where genreid="+id)
    return jsonify(data=res)

@app.route('/_year/<id>')
@login_required
def get_years(id):
    res=[]
    if id=='0':
        res=app.Sqlite3DB.query_db("select distinct year as name, year as id from mediafiles")
    else:
        res=app.Sqlite3DB.query_db("select * from mediafiles where year="+id)
    return jsonify(data=res)

@app.route('/_song/<id>')
@login_required
def get_song(id):
    res=app.Sqlite3DB.query_db("select 1 from mediafiles where id="+id)
    return jsonify(data=res)

@app.route('/_preload')
def preload():
    start = request.args.get('start', 1, type=int)
    count = request.args.get('count', 100, type=int)
    range = app.Sqlite3DB.query_db("select * from mediafiles limit "+start +', '+count)
    return jsonify(data=range)


@app.route('/getmedia/<filename>.flac')
@app.route('/getmedia/<filename>.ogg')
@app.route('/getmedia/<filename>.mp3')
@login_required
def send_file(filename):#TODO: rework
    """sends a music file"""
    try:
        idx = int(filename)
    except ValueError:
        abort(404)  #"404" #its a stub!!!
    our_file = app.Sqlite3DB.get_by_idx(idx)
    if our_file is None:
        abort(404)
    real_fullpath = our_file['fullpath']
    dir, fn = os.path.split(real_fullpath)
    return send_from_directory(dir, fn, as_attachment=True)

@app.route('/statistics')
@login_required
def view_stat():
    return render_template('statistics.html', Navigation=get_nav())

@app.route('/about')
@login_required
def view_about():
    return render_template('about.html', Navigation=get_nav())