##########################################################################################
##  This module is based on code from:												  ##
##						pytags - https://code.google.com/p/pytags/					##
##						quodlibet/ex falso - https://code.google.com/p/quodlibet/	 ##
##																					  ##
###																					###
## Because pytags requires external libraries i decided to write my own wrapper around  ##
## mutagen. So this class just maps different mutagen tags from different formats to	##
## properties like Album, Artist, Track and so on.									  ##
##########################################################################################
#LIBS
import sys, os, logging, mutagenx, json, datetime
#MODULES
from streamserver import app

#Set up log:
logging.basicConfig(format='%(filename)-20s:%(lineno)-5s %(levelname)-8s [%(asctime)s]  %(message)s',
                    level=app.Config.LOG_LEVEL)  #, filename ='streamserver.log'
Log = logging.getLogger(__name__)


class FileNotSupported(Exception):
    pass


class Tags:
    tag_groups = {
#id3
        "TCON":"genre",
        "TIT1":"grouping",
        "TIT2":"title",
        "TIT3":"version",
        "TPE1":"artist",
        "TPE2":"performer",
        "TPE3":"conductor",
        "TPE4":"arranger",
        "TEXT":"lyricist",
        "TCOM":"composer",
        "TENC":"encodedby",
        "TALB":"album",
        "TRCK":"tracknumber",
        "TPOS":"discnumber",
        "TSRC":"isrc",
        "TCOP":"copyright",
        "TPUB":"organization",
        "TSST":"discsubtitle",
        "TOLY":"author",
        "TMOO":"mood",
        "TBPM":"bpm",
        "TDRC":"date",
        "TDOR":"originaldate",
        "TOAL":"originalalbum",
        "TOPE":"originalartist",
        "WOAR":"website",
        "TSOP":"artistsort",
        "TSOA":"albumsort",
        "TSOT":"titlesort",
        "TSO2":"albumartistsort",
        "TSOC":"composersort",
        "TMED":"media",
        "TCMP":"compilation",

#flac
        "date":"date",
        "tracknumber":"tracknumber",
        "genre":"genre",
        "artist":"artist",
        "comment":"comment",
        "album":"album",
        "discid":"discid",
        "title":"title",

#apev2
        "subtitle":"version",
        "track":"tracknumber",
        "disc":"discnumber",
        "catalog":"labelid",
        "year":"date",
        "record location":"location",
        "album artist":"albumartist",
        "debut album":"originalalbum",
        "record date":"recordingdate",
        "original artist":"originalartist",
        "mixartist":"remixer",
#ape
        "Genre":"genre",
        "Year": "date",
        "Artist":"artist",
        "Album": "album",
        "Track": "tracknumber",
        "Title":"title",
#m4a
        b'\xa9nam': "title",
        b'\xa9ART': "artist",
        b'aART': "albumartist", #???
        b'\xa9alb': "album",
        b'trkn': "tracknumber",
        b'disk': "discnumber",
        b'\xa9gen':"genre",
        b'\xa9day': "date",
        b'cprt': "copyright",
        b'xid ' :"discid"
}

    def parse_mutagen_value(self,data):
        if isinstance(data,str):
            return data
        elif isinstance(data,tuple):
            var=list()
            var.append(str(i) for i in data)
            var=" ".join(var)
            return var
        elif isinstance(data,list):
            if isinstance(data[0],tuple):
                var=list()
                for i in data[0]: var.append(str(i))
                return " ".join(var)
            else:
                return " ".join(data)
        elif isinstance(data,mutagenx.apev2.APETextValue):
            return data.value
        else:
            if isinstance(data,mutagenx.id3.TDRC):
                return data.text[0].text
            else:
                return " ".join(data.text)

    def length_from_sec(self,seconds):
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        if h>0:
            return "%d:%02d:%02d" % (h, m, s)
        else:
            return "%02d:%02d" % (m, s)

    def get_length(self,mutagen_info,file,size):
        if hasattr(mutagen_info,'length'):
            length=self.length_from_sec(mutagen_info.length)
        else:
            bit=self.get_bitrate(mutagen_info,file,size)
            if bit>0:
                length=self.length_from_sec((size*8)/bit)
            else:
                length='<Unknown>'
        return length

    def get_bitrate(self, mutagen_info, file,size):
        if hasattr(mutagen_info, 'bitrate'):
            bit = mutagen_info.bitrate/1000
        else:
            if hasattr(mutagen_info, 'length'):
                bit = (size*8)/(mutagen_info.length*1000)
            else:
                bit=0 #TODO:proper bitrate and length
        return bit

    def __init__(self,file):
        self.filename = file
        self.mutagen_file = mutagenx.File(file)
        #self.format=type(self.mutagen_file)

        self.album = None
        self.artist = None
        self.title = None
        self.genre = None
        #if mutagenx.genres: self.genre=mutagen_file.genres
        self.tracknumber = None
        #self.discnumber = None
        self.date = None
        self.comment = None
        #self.copyright=None
        size = os.path.getsize(file)/1024/1024
        self.size=str("%.1f"%size)+' mb'
        #bitrate in 'xxx kbps'
        bit=self.get_bitrate(self.mutagen_file.info,file,size)
        if bit>0:
            self.bitrate=str("%.f" % bit)+" kbps"
        else:
            self.bitrate='<Unknown>'

        #length in 'h:m:s'
        self.length=self.get_length(self.mutagen_file.info,file,size)


        for key,value in self.mutagen_file.items():
            if key in self.tag_groups.keys():
                setattr(self, self.tag_groups[key], self.parse_mutagen_value(value))

