#Copyright(c) 2014, Konrad Sobon
# @arch_laboratory, http://archi-lab.net

import clr
clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *
#The inputs to this node will be stored as a list in the IN variable.
dataEnteringNode = IN

userStrings = IN[0]

if not any(isinstance(item, list) for item in userStrings):
	UVList = []
	for i in userStrings:
		strList = i.split(",")	
		UVList.append(UV.ByCoordinates(float(strList[0]), float(strList[1])))
else:
	UVList = [[] for i in range(len(userStrings))]
	for index, item in enumerate(userStrings):
		for i in item:
			strList = i.split(",")
			UVList[index].append(UV.ByCoordinates(float(strList[0]), float(strList[1])))

#Assign your output to the OUT variable
OUT = UVList
