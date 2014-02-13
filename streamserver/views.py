#LIBS
from flask import request,render_template,send_from_directory,abort,redirect#,jsonify
import os, logging
from lxml import etree

#MODULES
from streamserver import app, mediascanner,tagreader

#Logging
logging.basicConfig(format = u'%(filename)-20s:%(lineno)-5s %(levelname)-8s [%(asctime)s]  %(message)s',level=app.Config.LOG_LEVEL)#, filename ='streamserver.log'
Log = logging.getLogger(__name__)

#Navigation menu
Navigation=[
	{'caption':'Library', 'href':'/library'},
	{'caption':'Folders', 'href':'/folders'},
	{'caption':'Player',  'href':'#player'},
	{'caption':'Settings','href':'/settings'}
]
def getNavigation(requestpath):
	res=[]

	for d in Navigation:
		dtemp=d.copy()
		if dtemp['href']==requestpath:
			dtemp['active']=True
		res.append(dtemp)
	return res
@app.route('/test')
def test():
	xxxx=tagreader.Tags('d:\music\\test\\11 - Magnetrixx - Somnam.mp3')
	return repr(xxxx)
@app.route('/folders')
@app.route('/folders/<path>')
def folders(path=''):
	res=[]
	root=app.XMLDataBase.getroot()
	for child in root:
		if hasattr(child,'id'):
			id=child.id
		name=child.get("Name")
		href='/folders/'+child.get("Name")
		res.append({'name':name,'href':href})
	return render_template('folders.html',Navigation=getNavigation(request.path),Data=res)
@app.route('/library')
def library():
	return render_template('library.html',Navigation=getNavigation(request.path))
@app.route('/')
def index():
	"""return main template"""
	range=app.Sqlite3DB.get_range(500,25)
	res=[]
	for item in range:
		res.append({'id':item['id'],'name':item['filename'],'size':str(item['size']/1024/1024)+' mb','href':'getmedia/'+str(item['id'])+item['format']})
	#DataElement={'id':None,'name':None,'href':None,'size':None}
	return render_template('random.html',Navigation=getNavigation(request.path),Data=res)
	
@app.route('/_preload')
def preload():
	start = request.args.get('start', 1, type=int)
	count = request.args.get('count', 100, type=int)
	range=app.Sqlite3DB.get_range(start,count)
	res=[]
	print(range)
	for item in range:
		
		rec={}

		rec['id']=item['id']
		rec['name']=item['filename']
		rec['size']=str(item['size']/1024/1024)+' mb'
		rec['href']='getmedia/'+str(item['id'])+item['format']

		#rec.id=item['id']
		#rec.name=item['filename']
		#rec.size=str(item['size']/1024/1024)+' mb'
		#rec.href='getmedia/'+str(item['id'])+item['format']
		res.append(rec)
	return jsonify(data=res)
	
@app.route('/getmedia/<filename>.flac')
@app.route('/getmedia/<filename>.ogg')
@app.route('/getmedia/<filename>.mp3')
def send_file(filename):
	try:
		idx=int(os.path.splitext(filename)[0])
	except ValueError:
		abort(404) #"404" #its a stub!!!
	our_file=app.Sqlite3DB.get_by_idx(idx)
	if our_file==None:
		abort(404)
	real_fullpath=our_file['fullpath']
	dir,fn=os.path.split(real_fullpath) 
	return send_from_directory(dir,fn, as_attachment=True)

@app.route('/about')
def about():
	"""about page"""
	return render_template('about.html',Navigation=getNavigation(request.path))