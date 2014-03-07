#LIBS
from flask import Flask
from os import path, access, R_OK  # W_OK for write permission.
import logging

#Create app
app = Flask(__name__)
app.APP_ROOT = path.dirname(path.abspath(__file__))

#APP MODULES
import streamserver.config
app.Config = config
app.secret_key = 'some unique key'
import streamserver.serverdatabase
import streamserver.views
import streamserver.mediascanner
import streamserver.tagreader

#Set up log
if app.Config.LOG_LEVEL == 'DEBUG':
    app.Config.DEBUG = True
else:
    app.Config.DEBUG = False
logging.basicConfig(format='%(filename)-20s:%(lineno)-5s %(levelname)-8s [%(asctime)s]  %(message)s',
                    level=app.Config.LOG_LEVEL)  #, filename ='streamserver.log'
Log = logging.getLogger(__name__)

#GLOBALS
app.Sqlite3DB = None

def FileExistAccessSize(fname):
    if path.isfile(fname) and access(fname, R_OK) and (path.getsize(fname) > 0):
        return True
    else:
        return False

#Lets start:
Log.info("Starting StreamServer. LOG_LEVEL=%s", app.Config.LOG_LEVEL)
#if database exist and initialized:
if FileExistAccessSize(app.Config.SQLITE3_DATABASE_FILE):
    Log.info("Connecting to DB...")
    app.Sqlite3DB = serverdatabase.ServerDatabase()
    Log.info("Done.")
else:  # else reinitialize database
    Log.info("First DB initialization ...")
    app.Sqlite3DB = serverdatabase.ServerDatabase()
    app.Sqlite3DB.init_db()
    Log.info("Done.")
    Log.info("Preparing media library...")
    n=mediascanner.fullscan()
    Log.info("Done.")
