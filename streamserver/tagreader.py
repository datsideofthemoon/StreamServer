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
import sys,logging, mutagenx,json
#MODULES
from streamserver import app

#Set up log:
logging.basicConfig(format = u'%(filename)-20s:%(lineno)-5s %(levelname)-8s [%(asctime)s]  %(message)s',level=app.Config.LOG_LEVEL)#, filename ='streamserver.log'
Log = logging.getLogger(__name__)

class FileNotSupported(Exception):
	pass

#import mutagen.apev2


class APEv2File():
	# Map APE names to QL names. APE tags are also usually capitalized.
	# Also blacklist a number of tags.
	IGNORE = ["file", "index", "introplay", "dummy"]
	TRANS = {"subtitle": "version",
			"track": "tracknumber",
			"disc": "discnumber",
			"catalog": "labelid",
			"year": "date",
			"record location": "location",
			"album artist": "albumartist",
			"debut album": "originalalbum",
			"record date": "recordingdate",
			"original artist": "originalartist",
			"mixartist": "remixer",
	}
	#SNART = dict([(v, k) for k, v in iter(TRANS)])

	def __init__(self, filename):
		try:
			tag = mutagen.apev2.APEv2(filename)
		except mutagen.apev2.APENoHeaderError:
			tag = {}
		for key, value in tag.items():
			key = self.TRANS.get(key.lower(), key.lower())
			if (value.kind == mutagen.apev2.TEXT and key not in self.IGNORE):
				self[key] = "\n".join(list(value))
		#self.sanitize(filename)

class ID3File():
	IDS = {"TIT1": "grouping",
			"TIT2": "title",
			"TIT3": "version",
			"TPE1": "artist",
			"TPE2": "performer",
			"TPE3": "conductor",
			"TPE4": "arranger",
			"TEXT": "lyricist",
			"TCOM": "composer",
			"TENC": "encodedby",
			"TALB": "album",
			"TRCK": "tracknumber",
			"TPOS": "discnumber",
			"TSRC": "isrc",
			"TCOP": "copyright",
			"TPUB": "organization",
			"TSST": "discsubtitle",
			"TOLY": "author",
			"TMOO": "mood",
			"TBPM": "bpm",
			"TDRC": "date",
			"TDOR": "originaldate",
			"TOAL": "originalalbum",
			"TOPE": "originalartist",
			"WOAR": "website",
			"TSOP": "artistsort",
			"TSOA": "albumsort",
			"TSOT": "titlesort",
			"TSO2": "albumartistsort",
			"TSOC": "composersort",
			"TMED": "media",
			"TCMP": "compilation",
	}
	#SDI = dict([(v, k) for k, v in IDS.iteritems()])


	def CODECS(self):
		codecs = ["utf-8"]
		#codecs_conf = config.get("editing", "id3encoding")
		#codecs.extend(codecs_conf.strip().split())
		codecs.append("iso-8859-1")
		return codecs

	def __distrust_latin1(self, text, encoding):
		assert isinstance(text, unicode)
		if encoding == 0:
			text = text.encode('iso-8859-1')
			for codec in self.CODECS:
				try:
					text = text.decode(codec)
				except (UnicodeError, LookupError):
					pass
				else:
					break
			else:
				return None
		return text
		
	def __validate_name(self, k):
		"""Returns a ascii string or None if the key isn't supported"""
		if isinstance(k, unicode):
			k = k.encode("utf-8")
		if not (k and "=" not in k and "~" not in k
				and k.encode("ascii", "replace") == k):
			return
		return k
		
	def __init__(self, filename):
		tag = mutagen.id3.ID3(filename)

		for frame in tag.values():
			if frame.FrameID == "APIC" and len(frame.data):
				self.has_images = True
				continue
			elif frame.FrameID == "COMM" and frame.desc == "":
				name = "comment"
			elif frame.FrameID == "TMCL":
				for role, name in frame.people:
					key = self.__validate_name("performer:" + role)
					if key:
						self.add(key, name)
				continue
			else:
				name = self.IDS.get(frame.FrameID, "").lower()

			name = self.__validate_name(name)
			if not name:
				continue
			name = name.lower()

			id3id = frame.FrameID
			if id3id.startswith("T"):
				text = "\n".join(map(unicode, frame.text))
			elif id3id == "COMM":
				text = "\n".join(frame.text)
			elif id3id.startswith("W"):
				text = frame.url
				frame.encoding = 0
			else:
				continue

			if not text:
				continue
			text = self.__distrust_latin1(text, frame.encoding)
			if text is None:
				continue

			if name in self:
				self[name] += "\n" + text
			else:
				self[name] = text
			self[name] = self[name].strip()

			# to catch a missing continue above
			del name
		# foobar2000 writes long dates in a TXXX DATE tag, leaving the TDRC
		# tag out. Read the TXXX DATE, but only if the TDRC tag doesn't exist
		# to avoid reverting or duplicating tags in existing libraries.
		if audio.tags and "date" not in self:
			for frame in tag.getall('TXXX:DATE'):
				self["date"] = "\n".join(map(unicode, frame.text))

class Tags:
	def __init__(self, filenam):
		self.filename = filenam
		self.mutagen_file=mutagenx.File(filenam)
		#print(type(self.mutagen_file))
		#return self#setattr(o, "foo", "bar")

	def Album(self):
			return self.album
	def Artist(self):
			return self.artist
	def Vendor(self):
			return self.vendor
	def Title(self):
			return self.title
	def TrackTotal(self):
			return self.tracktotal
	def TrackNumber(self):
			return self.tracknumber
	def Genre(self):
			return self.genre
	def DiscNumber(self):
			return self.discnum
	def Date(self):
			return self.date
	def Comment(self):
			return self.comment
