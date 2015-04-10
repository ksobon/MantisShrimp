#Copyright(c) 2015, Konrad Sobon
# @arch_laboratory, http://archi-lab.net

import clr
import sys
clr.AddReference('ProtoGeometry')

pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

import os
appDataPath = os.getenv('APPDATA')
msPath = appDataPath + r"\Dynamo\0.7\packages\Mantis Shrimp\extra"
rhPath = appDataPath + r"\Dynamo\0.7\packages\Mantis Shrimp\bin"
rhDllPath = appDataPath + r"\Dynamo\0.7\packages\Mantis Shrimp\bin\Rhino3dmIO.dll"
if msPath not in sys.path:
	sys.path.Add(msPath)
if rhPath not in sys.path:
	sys.path.Add(rhPath)
	clr.AddReferenceToFileAndPath(rhDllPath)

from Autodesk.DesignScript.Geometry import *
import Rhino as rc

#The inputs to this node will be stored as a list in the IN variable.
dataEnteringNode = IN
rhObjects = IN[0]
keys = IN[1]

#extract all user strings from rhino object

userStrings = []
for i, key in zip(rhObjects, keys):
	try:
		item = i.Geometry
	except:
		pass
	if item == None:
		item = i
	userSubStrings = []
	for i in range(0, len(key),1):
		userSubStrings.extend(item.GetUserStrings().GetValues(key[i]))
	userStrings.append(userSubStrings)

#Assign your output to the OUT variable
OUT = userStrings
