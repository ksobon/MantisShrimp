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

import Rhino as rc
from Autodesk.DesignScript.Geometry import *
import math

#The inputs to this node will be stored as a list in the IN variable.
dataEnteringNode = IN
rhObjects = IN[0]
keys = IN[1]

#extract all user strings from rhino object
geometry = rhObjects[0]
try:
	geometry = rhObjects[0].Geometry
except:
	pass
if not any(isinstance(item, list) for item in keys):
	userStrings = []
	for key in keys:
		userStrings.extend(geometry.GetUserStrings().GetValues(key))
else:
	userStrings = [[] for i in range(len(rhObjects))]
	for index, item in enumerate(rhObjects):
		for key in keys[index]:
			userStrings[index].extend(item.GetUserStrings().GetValues(key))

#Assign your output to the OUT variable
OUT = userStrings
