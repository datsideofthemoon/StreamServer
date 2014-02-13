#LIBS
from flask import Flask, render_template
from os import path, access, R_OK  # W_OK for write permission.
from lxml import etree
import logging
#Create app
app = Flask(__name__)
app.APP_ROOT = path.dirname(path.abspath(__file__))

#APP MODULES
import streamserver.config
app.Config=config
import streamserver.serverdatabase
import streamserver.views
import streamserver.mediascanner
import streamserver.tagreader
#Set up log
if app.Config.LOG_LEVEL=='DEBUG':
	app.Config.DEBUG=True
else:
	app.Config.DEBUG=False
logging.basicConfig(format = u'%(filename)-20s:%(lineno)-5s %(levelname)-8s [%(asctime)s]  %(message)s',level=app.Config.LOG_LEVEL)#, filename ='streamserver.log'
Log = logging.getLogger(__name__)

#GLOBALS
app.Sqlite3DB=None
app.XMLDataBase=None
def FileExistAccessSize(fname):
	if path.isfile(fname) and access(fname, R_OK) and (path.getsize(fname)>0):
		return True
	else:
		return False

#Lets begin:		
Log.info("Starting StreamServer. LOG_LEVEL=%s",app.Config.LOG_LEVEL)
#if database exist and initialized:
if FileExistAccessSize(app.Config.SQLITE3_DATABASE_FILE) and FileExistAccessSize(app.Config.XML_DATABASE_FILE) :
	Log.info("Connecting to DB...")
	app.Sqlite3DB=serverdatabase.ServerDatabase()
	Log.info("Done.")
	app.XMLDataBase=etree.parse(app.Config.XML_DATABASE_FILE)
else: #else reinitialize database
	Log.info("First DB initialization ...")
	app.Sqlite3DB=serverdatabase.ServerDatabase()
	app.Sqlite3DB.init_db()
	Log.info("Done.")
	Log.info("Preparing media library...")
	app.XMLDataBase=etree.ElementTree(mediascanner.ScanMediaLibrary())
	Log.info("Done.")
	Log.info("Writing XML database...")
	app.XMLDataBase.write(app.Config.XML_DATABASE_FILE,encoding='utf-8',pretty_print=True)
	Log.info("Done.")
	
	
	