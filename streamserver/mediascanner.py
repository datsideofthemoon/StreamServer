# -*- coding: utf-8 -*-
#LIBS
import sys, os, logging
from fnmatch import fnmatch
from lxml import etree
#MODULES
from streamserver import app, tagreader

#Set up log:
logging.basicConfig(format='%(filename)-20s:%(lineno)-5s %(levelname)-8s [%(asctime)s]  %(message)s',
                    level=app.Config.LOG_LEVEL)  #, filename ='streamserver.log'
Log = logging.getLogger(__name__)

#GLOBALS
mediatypes = app.Config.MEDIA_TYPES

mediafiles_values = []  #this is for insert many rows

#Database fields, don't need this, but want for WYSIWYG coding
mediafiles_flds = ('filename',
                   'fullpath',
                   'directory',
                   'parentid',
                   'size',
                   'format',
                   'length',
                   'bitrate',
                   'tn',
                   'title',
                   'genreid',
                   'artistid',
                   'albumid',
                   'year',
                   'comment')
artists_flds = ('id', 'artist')
albums_flds = ('id', 'album', 'artistid')
genres_flds = ('id', 'genre')
years_flds = ('year')

def add_file(path, name, parentid):
    fullpath = os.path.join(path, name)
    directory = os.path.basename(os.path.normpath(path))
    format = os.path.splitext(name)[1]

    tags = tagreader.Tags(fullpath)

    size=tags.size
    length = tags.length
    bitrate = tags.bitrate
    if  tags.tracknumber:
        tn = tags.tracknumber.strip(' \t\n\r')
    else:
        tn=None

    if tags.title:
        title = tags.title.strip(' \t\n\r')
    else:
        title = None

    if tags.genre:
        genre = tags.genre.strip(' \t\n\r')
    else:
        genre = None

    if tags.artist:
        artist = tags.artist.strip(' \t\n\r')
    else:
        artist = None

    if tags.album:
        album = tags.album.strip(' \t\n\r')
    else:
        album = None

    if tags.date:
        year = tags.date.strip(' \t\n\r')
    else:
        year = None

    if tags.comment:
        comment = tags.comment.strip(' \t\n\r')
    else:
        comment = None

    if not title or title=='':   title = '<Unknown>'
    if not genre or genre =='': genre = '<Unknown>'
    if not artist or artist=='': artist = '<Unknown>'
    if not album or album=='': album = '<Unknown>'
    if not year or year=='': year='<Unknown>'
    if not comment : comment=''
    genreid = app.Sqlite3DB.get_or_ins_genre(genre)
    artistid = app.Sqlite3DB.get_or_ins_artist(artist)
    albumid = app.Sqlite3DB.get_or_ins_album(album,artistid)

    values = (
        name, fullpath, directory, parentid, size, format, length, bitrate, tn, title, genreid, artistid, albumid, year,
        comment)

    mediafiles_values.append(values)
    return len(mediafiles_values)


def recursive_scan(somedir, parentid):#TODO: need to skip insert empty dirs(e.g. where are no media files)
    dirname = os.path.basename(os.path.normpath(somedir))
    dirid = app.Sqlite3DB.insert_dir(parentid, dirname)
    xml_dir = etree.Element('dir', Name=dirname)
    for item in os.listdir(somedir):
        fullpath = os.path.join(somedir, item)
        if os.path.isfile(fullpath):
            for filetype in mediatypes:
                if fnmatch(fullpath, filetype):
                    idx = add_file(somedir, item, dirid)
                    xml_file = etree.Element('file', id=str(idx))
                    xml_file.text = item
                    xml_dir.append(xml_file)
        else:  #item is dir
            xml_dir.append(recursive_scan(fullpath, dirid))
    return xml_dir


def fullscan():
    tree_root = etree.Element('root')
    for dir in app.Config.MUSIC_LIB:
        tree_root.append(recursive_scan(dir, 0))
    if app.Sqlite3DB.insert_many('mediafiles', mediafiles_flds, mediafiles_values):
        Log.info("Fullscan done, inserted %s mediafiles." % len(mediafiles_values))
    #print(n)
    return tree_root
