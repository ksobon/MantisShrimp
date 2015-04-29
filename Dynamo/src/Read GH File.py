#Copyright(c) 2015, Konrad Sobon
# @arch_laboratory, http://archi-lab.net

import clr
import sys
clr.AddReference('ProtoGeometry')

pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

import os
appDataPath = os.getenv('APPDATA')
msPath = appDataPath + r"\Dynamo\0.8\packages\Mantis Shrimp\extra"
rhPath = appDataPath + r"\Dynamo\0.8\packages\Mantis Shrimp\bin"
rhDllPath = appDataPath + r"\Dynamo\0.8\packages\Mantis Shrimp\bin\Rhino3dmIO.dll"
if msPath not in sys.path:
	sys.path.append(msPath)
if rhPath not in sys.path:
	sys.path.append(rhPath)
	clr.AddReferenceToFileAndPath(rhDllPath)

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

# recursive function to process any input list and output 
# matching structure list
def ProcessList(_func, _list):
    return map( lambda x: ProcessList(_func, x) if type(x)==list else _func(x), _list)
    
# function to convert MS Objects to DS objects
def toDSObject(item):
	if type(item) == MSPoint:
		return item.toDSPoint()
	elif type(item) == MSLine:
		return item.toDSLine()
	elif type(item) == MSPolyLine:
		return item.toDSPolyCurve()
	elif type(item) == MSEllipse:
		return item.toDSEllipse()
	elif type(item) == MSCircle:
		return item.toDSCircle()
	elif type(item) == MSArc:
		return item.toDSArc()
	elif type(item) == MSNurbsCurve:
		return item.toDSNurbsCurve()
	elif type(item) == MSMultiSpanNurbsCurve:
		return item.toDSPolyCurve()
	elif type(item) == MSPolyCurve:
		return item.toDSPolyCurve()
	elif type(item) == MSMesh:
		return item.toDSMesh()
	elif type(item) == MSNurbsSurface:
		return item.toDSNurbsSurface()
	else:
		message = "Geometry type not yet supported"
		return message

message = None
if _import:
	serializedData = serializer.data
	if type(serializedData) == MSData:
		geometryOut = serializedData.data
	else:
		geometryOut = ProcessList(toDSObject, serializedData)
else:
	message = "Import set to false"

#Assign your output to the OUT variable
if message == None:
	OUT = geometryOut
else:
	OUT = '\n'.join('{:^35}'.format(s) for s in message.split('\n'))
