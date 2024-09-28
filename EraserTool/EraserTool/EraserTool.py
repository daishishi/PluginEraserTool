from krita import *
from PyQt5.QtWidgets import QMessageBox
from enum import Enum
import os
import json
import xml.etree.ElementTree as ET


class EraserTool(krita.Extension):
	def __init__(self, parent):
		super(EraserTool, self).__init__(parent)

		self.brushList : list = []
		self.eraserList : list = []
		self.brush : str = None
		self.eraser : str = None
		self.enumBrush : Enum = Enum('enumBrush', ['Brush', 'Eraser'])
		self.brushState : Enum = self.enumBrush.Brush
		self.presetsFile : str = os.path.join(QStandardPaths.writableLocation(QStandardPaths.GenericConfigLocation), 'pet-Presets.json')


	def changeResource(self):
		# Check wich type of brush it is and save accordinly (Eraser or Brush)
		#self.brush = Application.activeWindow().activeView().currentBrushPreset().name()
		currentPreset = Application.activeWindow().activeView().currentBrushPreset()
		if not currentPreset:
			return

		if self.brush and self.brush.name() == currentPreset.name():
			self.brushState = self.enumBrush.Brush
			return
		elif self.eraser and self.eraser.name() == currentPreset.name():
			self.brushState = self.enumBrush.Eraser
			return

		if currentPreset.name() in self.brushList:
			self.brushState = self.enumBrush.Brush
			self.brush = currentPreset
			#print(currentPreset)
		elif currentPreset.name() in self.eraserList:
			self.brushState = self.enumBrush.Eraser
			self.eraser = currentPreset
			#print(currentPreset)


	def setup(self):
		pass


	def createActions(self, window):
		self.newActions(window)
		# Trying to access Krita's internal resources earlier than this function
		# leads to errors. So reading / creating the brushes list was put here.
		if not self.readSettings():
			self.updateBrushList()
			return
		self.compareList()


	def readSettings(self):

		allPresetName = list(Application.resources('preset').keys())
		jsonDict = None

		if os.path.isfile(self.presetsFile):
			with open(self.presetsFile, 'r') as file:
				try:
					fileStr = file.read()
				except Exception as e:
					print('Could not open the file')
					return False

				try:
					jsonDict = json.loads(fileStr)
				except Exception as e:
					print('Could not parse')
					return False
		else:
			print('no file')
			return False

		for key in jsonDict:
			if key == "LastBrush":
				presetName = jsonDict[key]
				if presetName in allPresetName:
					self.brush = Application.resources('preset')[presetName]
				else:
					firstBrush = "b) Basic-1"
					self.brush = Application.resources('preset')[firstBrush]

			elif key == "LastEraser":
				presetName = jsonDict[key]
				if presetName in allPresetName:
					self.eraser = Application.resources('preset')[presetName]
				else:
					firstEraser = "a) Eraser Circle"
					self.eraser = Application.resources('preset')[firstEraser]

			elif key == 'Brushes':
				self.brushList = jsonDict[key]

			elif key == 'Erasers':
				self.eraserList = jsonDict[key]

		return True


	def compareList(self):
		allPresetName = list(Application.resources('preset').keys())
		savedPresetName = self.brushList + self.eraserList
		allPresetName.sort()
		savedPresetName.sort()

		if allPresetName == savedPresetName:
			#print('No change')
			return True
		else:
			#print('Brushes changed')
			self.updateBrushList()


	def updateBrushList(self):
		#print('Updating')
		self.brushList = []
		self.eraserList = []
		allBrushes = Application.resources('preset')

		for preset in allBrushes.keys():
			brushXML = Preset(allBrushes[preset]).toXML()
			#brushParsed = ET.fromstring(brushXML)
			
			try:
				brushParsed = ET.fromstring(brushXML)
			except Exception:
				cleanBrushXML = ''
				for key in brushXML:
					if not key.isprintable():
						continue
					cleanBrushXML += key
				brushParsed = ET.fromstring(cleanBrushXML)
			
			BlendMode = None
			EraserMode = None

			for id, child in enumerate(brushParsed):
				param = brushParsed[id].get('name')
				if param == 'CompositeOp':
					BlendMode = child.text
				elif param == 'EraserMode':
					EraserMode = child.text
				if BlendMode and EraserMode:
					break

			if BlendMode == 'erase' or EraserMode == 'true':
				self.eraserList.append(preset)
			else:
				self.brushList.append(preset)


	def saveSettings(self):
		lastBrush = self.brush
		lastEraser = self.eraser

		if lastBrush:
			lastBrush = self.brush.name()
		if lastEraser:
			lastEraser = self.eraser.name()

		x = {
			"LastBrush" : lastBrush,
			"LastEraser" : lastEraser,
			"Brushes" : self.brushList,
			"Erasers" : self.eraserList
			}
		with open(self.presetsFile, 'w') as file:
			try:
				file.write(json.dumps(x, indent=4))
			except Exception as e:
				print('Not able to save')


	def newActions(self, window):
		action1 = window.createAction("activate_slot_brush", "last brush", "")
		action1.triggered.connect(self.selectBrush)
		action2 = window.createAction("activate_slot_eraser", "last eraser", "")
		action2.triggered.connect(self.selectEraser)
		action3 = window.createAction("update_preset_list", "update preset list", "")
		action3.triggered.connect(self.updateBrushList)
		action4 = window.createAction("swap_slot", "swap slot", "")
		action4.triggered.connect(self.swapSlot)


	def selectBrush(self):
		Application.action("KritaShape/KisToolBrush").trigger()
		currentView = Application.activeWindow().activeView()
		if self.brush:
			currentView.setCurrentBrushPreset(self.brush)
			self.brushState = self.enumBrush.Brush


	def selectEraser(self):
		Application.action("KritaShape/KisToolBrush").trigger()
		currentView = Application.activeWindow().activeView()
		if self.eraser:
			currentView.setCurrentBrushPreset(self.eraser)
			self.brushState = self.enumBrush.Eraser


	def swapSlot(self):
		Application.action("KritaShape/KisToolBrush").trigger()
		currentView = Application.activeWindow().activeView()
		# Check which slot is active, using Enums, then swap to the other slot.
		if self.brushState == self.enumBrush.Eraser:
			self.selectBrush()
		else:
			self.selectEraser()


	def errorMessage(self, message):
		newDialog = QMessageBox()
		newDialog.setWindowTitle("Initializing error")
		newDialog.setText(message)
		newDialog.exec_()


	def connecting(self):
		presetDockerNames = ['ResourceChooser','wdgPresetChooser']
		qwin = Krita.instance().activeWindow().qwindow()
		for name in presetDockerNames:
			obj1 = qwin.findChild(QWidget, name)
			if not obj1:
				continue
			else: break
		if not obj1:
			self.errorMessage("The Brush Docker wasn't found.\nPlease, contact the developer.")
			return
		
		try:
			obj2 = obj1.findChild(QListView,'ResourceItemview')
			obj2.currentResourceChanged.disconnect(self.changeResource)
		except Exception as e:
			print('UI not connected')

		if not obj2:
			self.errorMessage("The Brushes inside the Docker couldn't be found.\nPlease, contact the developer.")
			return
		obj2.currentResourceChanged.connect(self.changeResource)
