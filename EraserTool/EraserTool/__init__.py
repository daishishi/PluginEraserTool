from .EraserTool import *
from krita import *
import re

versionRequired = [5, 2, 0]
plugin = EraserTool(Application)


def kritaVersion():
	returned={
	        'major': 0,
	        'minor': 0,
	        'revision': 0,
	        'devFlag': '',
	        'git': '',
	        'rawString': Krita.instance().version()
	    }

	nfo=re.match("(\d+)\.(\d+)\.(\d+)(?:-([^\s]+)\s\(git\s([^\)]+)\))?", returned['rawString'])
	if not nfo is None:
		returned['major']=int(nfo.groups()[0])
		returned['minor']=int(nfo.groups()[1])
		returned['revision']=int(nfo.groups()[2])
		returned['devFlag']=nfo.groups()[3]
		returned['git']=nfo.groups()[4]

	return returned


def checkKritaVersion(major, minor, revision):
	nfo = kritaVersion()

	if nfo['major'] == major:
		if nfo['minor'] == minor:
			if revision is None or nfo['revision'] >= revision:
				return True
		elif nfo['minor'] > minor:
			return True
	elif nfo['major'] > major:
		return True
	return False



class notifier(krita.Notifier):
	def __init__(self, parent):
		super(notifier, self).__init__(parent)
		self.imageCreated.connect(self.conectado)
		self.applicationClosing.connect(self.saving)


	def conectado(self):
		plugin.connecting()


	def saving(self):
		plugin.saveSettings()


if not checkKritaVersion(5,2,0):
	print('Version not valid')
else:
	print('Version valid')
	Scripter.addExtension(plugin)
	notifier(Application)
