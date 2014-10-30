#Copyright(c) 2014, Konrad Sobon
# @arch_laboratory, http://archi-lab.net

import clr
import sys
clr.AddReference('ProtoGeometry')

pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)
import pickle
import os
rhCommonFile = r'C:\Program Files\Rhinoceros 5 (64-bit)\System\RhinoCommon.dll'
if os.path.exists(rhCommonFile):
	RhinoCommonPath = r'C:\Program Files\Rhinoceros 5 (64-bit)\System'
	if RhinoCommonPath not in sys.path:
		sys.path.Add(RhinoCommonPath)
	clr.AddReferenceToFileAndPath(RhinoCommonPath + r"\RhinoCommon.dll")
	import Rhino as rc
	message = None
else:
	message = "RhinoCommon.dll not located in \nC:\Program Files\Rhinoceros 5 \n(64-bit)\System. Please change \nRhinoCommonPath variable."

from Autodesk.DesignScript.Geometry import *
from System import Array
from System.Collections.Generic import *

#The inputs to this node will be stored as a list in the IN variable.
dataEnteringNode = IN
filePath = str(IN[0])

class SerializeObjects(object):
	def __init__(self, filePath, data = None):
		self.filePath = filePath
		self.data = data

	def saveToFile(self):
		with open(self.filePath, 'wb') as outf:
			pickle.dump(self.data, outf)

	def readFromFile(self):
		with open(self.filePath, 'rb') as inf:
			self.data = pickle.load(inf)

serializer = SerializeObjects(filePath)
serializer.readFromFile()

#Assign your output to the OUT variable
if message != None:
	OUT = '\n'.join('{:^35}'.format(s) for s in message.split('\n'))
else:
	OUT = serializer.data
