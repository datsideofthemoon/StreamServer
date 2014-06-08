#LIBS
import sqlite3, logging
from flask import g
from contextlib import closing
from os import path
import io

#MODULES
from streamserver import app

#Set up log:
logging.basicConfig(format='%(filename)-20s:%(lineno)-5s %(levelname)-8s [%(asctime)s]  %(message)s',
                    level=app.Config.LOG_LEVEL)  #, filename ='streamserver.log'
Log = logging.getLogger(__name__)


class ServerDatabase:
    def insert_dir(self, parentid,dir):
        query = 'insert into directories (parentid, directory) values (?, ?)'
        with app.app_context():
            db = self.get_db()
            cur = db.cursor()
            cur.execute(query, (parentid, dir))
            idx = cur.lastrowid
            db.commit()
            cur.close()
        return idx

    def get_or_ins_album(self, album,artistid):
        query1 = 'insert into albums (album, artistid) values (?, ?)' #or ignore

        with app.app_context():
            db = self.get_db()
            cur = db.cursor()
            try:
                cur.execute(query1, (album,artistid))
                idx = cur.lastrowid
            except:
                query2 = 'SELECT id FROM albums where album=(?)'
                idx=cur.execute(query2, (album,))
                idx=cur.fetchone()['id']
            db.commit()
            cur.close()
        return idx

    def get_or_ins_artist(self, value):
        query1 = 'insert into artists (artist) values (?)' #or ignore

        with app.app_context():
            db = self.get_db()
            cur = db.cursor()
            try:
                cur.execute(query1, (value,))
                idx = cur.lastrowid
            except:
                query2 = 'SELECT id FROM artists where artist=(?)'
                idx=cur.execute(query2, (value,))
                idx=cur.fetchone()['id']
            db.commit()
            cur.close()
        return idx

    def get_or_ins_genre(self, value):
        query1 = 'insert into genres (genre) values (?)' #or ignore

        with app.app_context():
            db = self.get_db()
            cur = db.cursor()
            try:
                cur.execute(query1, (value,))
                idx = cur.lastrowid
            except:
                query2 = 'SELECT id FROM genres where genre=(?)'
                idx=cur.execute(query2, (value,))
                idx=cur.fetchone()['id']
            db.commit()
            cur.close()
        return idx

    def insert_many(self, table, fields=(), values=[]):
        try:
            with app.app_context():
                db = self.get_db()
                cur = db.cursor()
                query = 'INSERT INTO %s (%s) VALUES (%s)' % (table, ', '.join(fields), ', '.join(['?'] * len(fields)))
                cur.executemany(query, values)
                db.commit()
                #id = cur.lastrowid
                cur.close()
                return True
        except:
            return False

    def insert(self, table, fields=(), values=()):
        with app.app_context():
            db = self.get_db()
            cur = db.cursor()
            query = 'INSERT INTO %s (%s) VALUES (%s)' % (
                table,
                ', '.join(fields),
                ', '.join(['?'] * len(values))
            )
            cur.execute(query, values)
            db.commit()
            id = cur.lastrowid
            cur.close()
            return id

    def get_range(self, start, count):
        return self.query_db('select * FROM mediafiles WHERE id >= (%s) AND id <= (%s)' % (start, start + count - 1),
                             one=False)

    def get_by_idx(self, idx):#TODO: refactoring here
        max =self.query_db('select Count(*) from mediafiles',one=True)['Count(*)']
        max=max
        if (0 < idx) and (idx <= max) and (max >= 1):
            return self.query_db('select * FROM mediafiles WHERE id = (%s)' % idx, one=True)
        else:
            return None

    def get_library(self):
        return self.query_db('select * from mediafiles')

    #@app.teardown_appcontext
    def close_connection(self):
        #with app.app_context():
        db = getattr(g, '_database', None)
        if db is not None:
            db.close()

    def query_db(self, query, args=(), one=False):
        cur = self.get_db().execute(query, args)
        rv = cur.fetchall()
        cur.close()
        #print(rv)
        return (rv[0] if rv else None) if one else rv

    def get_db(self):
        with app.app_context():
            db = getattr(g, '_database', None)
            if db is None:
                db = g._database = self.connect_db()
        return db

    def init_db(self):
        with closing(self.connect_db()) as db:
            with io.open(path.join(app.APP_ROOT, 'schema.sql'), 'r') as f:
                schema = f.read()
                db.cursor().executescript(schema)
            db.commit()

    def dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def enable_foreign_keys(self):
        cur = self.get_db().cursor()
        rows = cur.execute('PRAGMA foreign_keys')
        for row in rows:
            Log.debug("Database PRAGMA FOREIGN_KEYS was: " + str(row['foreign_keys']))
            if row['foreign_keys'] == 0:
                cur.execute('PRAGMA foreign_keys=ON')
                rws = cur.execute('PRAGMA foreign_keys')
                for rw in rws:
                    if rw['foreign_keys'] == 0:
                        raise Exception(
                            "Database PRAGMA FOREIGN_KEYS CANNOT BE TURNED ON! Recompile sqlite3 with FOREIGN_KEYS on.")
                    else:
                        Log.debug("Database PRAGMA FOREIGN_KEYS now is: " + str(rw['foreign_keys']))
                    return True
            else:
                return True

    def connect_db(self):
        db = sqlite3.connect(app.Config.SQLITE3_DATABASE_FILE)
        db.row_factory = self.dict_factory
        return db

    def __init__(self):
        with app.app_context():
            g._database = self.connect_db()
            self.enable_foreign_keys()

