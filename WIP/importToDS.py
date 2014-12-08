#Copyright(c) 2014, Konrad Sobon
# @arch_laboratory, http://archi-lab.net

import clr
import sys
clr.AddReference('ProtoGeometry')

RhinoCommonPath = r'C:\Program Files\Rhinoceros 5 (64-bit)\System'
if RhinoCommonPath not in sys.path:
	sys.path.Add(RhinoCommonPath)
clr.AddReferenceToFileAndPath(RhinoCommonPath + r"\RhinoCommon.dll")

pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

ms_path = r'C:\Users\ksobon\AppData\Roaming\Dynamo\0.7\packages\Mantis Shrimp\extra'
if ms_path not in sys.path:
	sys.path.Add(ms_path)

from Autodesk.DesignScript.Geometry import *
from System import Array
from System.Collections.Generic import *
import Rhino as rc
import pickle
from mantisshrimp import *

#The inputs to this node will be stored as a list in the IN variable.
dataEnteringNode = IN
filePath = str(IN[0])
_import = IN[1]

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

geometryOut = []
if _import:
	for item in serializer.data:
		if type(item) == MSPoint:
			geometryOut.append(item.toDSPoint())
		elif type(item) == MSLine:
			geometryOut.append(item.toDSLine())
		elif type(item) == MSPolyLine:
			geometryOut.append(item.toDSPolyCurve())
		elif type(item) == MSEllipse:
			geometryOut.append(item.toDSEllipse())
		elif type(item) == MSCircle:
			geometryOut.append(item.toDSCircle())
		elif type(item) == MSArc:
			geometryOut.append(item.toDSArc())
		elif type(item) == MSNurbsCurve and item.spanCount == 1:
			geometryOut.append(item.toDSSingleSpanNurbsCurve())
		elif type(item) == MSMesh:
			geometryOut.append(item.toDSMesh())
		elif type(item) == MSData:
			geometryOut.append(item.data)
		elif type(item) == MSNurbsSurface:
			geometryOut.append(item.toDSNurbsSurface())
		else:
			geometryOut.append("Geometry type not yet supported")

#Assign your output to the OUT variable
OUT = geometryOut
