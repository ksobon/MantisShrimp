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

#convert rhino/gh geometry to ds geometry
strings = []
for i in rhObjects:
	try:
		i = i.Geometry
	except:
		pass
	keys = i.GetUserStrings().AllKeys
	for index in range(0, len(keys), 1):
		strings.extend(i.GetUserStrings().GetValues(keys[index]))

#Assign your output to the OUT variable
OUT = strings
