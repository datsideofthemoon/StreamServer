# -*- coding: utf-8 -*-
#LIBS
import sys,os,logging, mutagen, jsonpickle,sqlite3
from fnmatch import fnmatch
from lxml import etree
#MODULES
from streamserver import app

#Set up log:
logging.basicConfig(format = u'%(filename)-20s:%(lineno)-5s %(levelname)-8s [%(asctime)s]  %(message)s',level=app.Config.LOG_LEVEL)#, filename ='streamserver.log'
Log = logging.getLogger(__name__)

#Get proper fs and set script encoding
from imp import reload
reload (sys)
sys_enc=sys.getfilesystemencoding()

#sys.setdefaultencoding("utf-8")

#GLOBALS
mediatypes = app.Config.MEDIA_TYPES#.decode(sys_enc)

DB_as_list=[] #this is for mega-large query in the end of scanning

#Database fields, don't need this, but for best WYSIWYG coding
mediafiles_flds=('filename','fullpath','directory','size','format','bitrate','tn','track','genreid','artistid','albumid','year','comment')
artists_flds=('id','artist')
albums_flds=('id','album','artist')
genres_flds=('id','genre')
years_flds=('year')




def AddFileToDB(path,name):
	#filename = name.decode(sys_enc)
	fullpath = os.path.join(path,name)
	#fullpath=os.path.join(path,name)
	#read metadata from file
	#metadata = mutagen.File(fullpath,easy=False)
	#if mutagen cannot read file then skip adding this file
	#if metadata==None:
	#	return
	
	directory = os.path.basename(os.path.normpath(path))
	size = os.path.getsize(fullpath) ##-here was many errors
	format = os.path.splitext(name)[1]
	bitrate = 0#metadata['bitrate'] if 'bitrate' in metadata else 0
	#if "COMM:iTunNORM:'eng'" in metadata: del metadata["COMM:iTunNORM:'eng'"]
	#if "COMM:iTunSMPB:'eng'" in metadata: del metadata["COMM:iTunSMPB:'eng'"]
	#if "COMM:iTunPGAP:'eng'" in metadata: del metadata["COMM:iTunPGAP:'eng'"]
	#print(metadata)
	tn=0
	track=None
	genre=None
	artist=None
	album=None
	year=None
	comment=None
	values=(name,fullpath,directory,size,format,bitrate,tn,track,genre,artist,album,year,comment)
	DB_as_list.append(values)
	return len(DB_as_list)

def RecursiveScan(somedir):
	dirname=os.path.basename(os.path.normpath(somedir))
	xml_dir=etree.Element(u'dir', Name=dirname)	
	for item in os.listdir(somedir):
		fullpath = os.path.join(somedir,item)
		if os.path.isfile(fullpath): 
			for filetype in mediatypes:
				if fnmatch(fullpath, filetype):
					idx=AddFileToDB(somedir,item)
					xml_file=etree.Element(u'file',id=str(idx))
					xml_file.text=item
					xml_dir.append(xml_file)
		else: #item is dir
			xml_dir.append(RecursiveScan(fullpath))
	return xml_dir

def ScanMediaLibrary():
	tree_root=etree.Element(u'root')
	for dir in app.Config.MUSIC_LIB:
		tree_root.append(RecursiveScan(dir))
	x=app.Sqlite3DB.insert_many('mediafiles',mediafiles_flds,DB_as_list)
	return tree_root
