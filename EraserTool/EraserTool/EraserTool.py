#-----------------------------------------------------------------------------
# PluginEraserTool
# Copyright (C) 2022 - Daishishi
# -----------------------------------------------------------------------------
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.
# If not, see https://www.gnu.org/licenses/
# -----------------------------------------------------------------------------
# A Krita plugin created to mimick a dedicated Eraser Tool
# -----------------------------------------------------------------------------

from krita import *
import os
import json
import xml.etree.ElementTree as ET


class EraserTool(krita.Extension):
	def __init__(self, parent):
		super(EraserTool, self).__init__(parent)
		self.brushList = []
		self.eraserList = []
		self.brush = None
		self.eraser = None
		self.presetsFile = os.path.join(QStandardPaths.writableLocation(QStandardPaths.GenericConfigLocation), 'pet-Presets.json')


	def changeResource(self):
		# Check wich type of brush it is and save accordinly (Eraser or Brush)
		#self.brush = Application.activeWindow().activeView().currentBrushPreset().name()
		currentPreset = Application.activeWindow().activeView().currentBrushPreset()
		if not currentPreset:
			return

		if self.brush and self.brush.name() == currentPreset.name():
			return
		elif self.eraser and self.eraser.name() == currentPreset.name():
			return

		if currentPreset.name() in self.brushList:
			self.brush = currentPreset
			#print(currentPreset)
		elif currentPreset.name() in self.eraserList:
			self.eraser = currentPreset
			#print(currentPreset)


	def setup(self):
		pass


	def createActions(self, window):
		self.newActions(window)
		# Trying access Krita's internal resources earlier than this function
		# leads to errors. So reading / creating the brushes list was put here.
		if not self.readSettings():
			self.updateBrushList()
			return
		self.compareList()


	def readSettings(self):

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
				if presetName:
					self.brush = Application.resources('preset')[presetName]
				else:
					firstBrush = "b) Basic-1"
					self.brush = Application.resources('preset')[firstBrush]
			elif key == "LastEraser":
				presetName = jsonDict[key]
				if presetName:
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
			brushParsed = ET.fromstring(brushXML)
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


	def selectBrush(self):
		Application.action("KritaShape/KisToolBrush").trigger()
		currentView = Application.activeWindow().activeView()
		if self.brush:
			currentView.setCurrentBrushPreset(self.brush)
		else:
			pass
		#print(self.brush)


	def selectEraser(self):
		Application.action("KritaShape/KisToolBrush").trigger()
		currentView = Application.activeWindow().activeView()
		if self.eraser:
			currentView.setCurrentBrushPreset(self.eraser)
		#print(self.eraser)


	def connecting(self):
		qwin = Krita.instance().activeWindow().qwindow()
		obj1 = qwin.findChild(QWidget, 'ResourceChooser')
		obj2 = obj1.findChild(QListView,'ResourceItemview')
		obj2.currentResourceChanged.disconnect()

		obj2.currentResourceChanged.connect(self.changeResource)