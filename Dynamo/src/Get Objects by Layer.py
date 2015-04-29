#Copyright(c) 2015, Konrad Sobon
# @arch_laboratory, http://archi-lab.net

import clr
import sys
clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *

pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

import os
appDataPath = os.getenv('APPDATA')
msPath = appDataPath + r"\Dynamo\0.8\packages\Mantis Shrimp\extra"
rhPath = appDataPath + r"\Dynamo\0.8\packages\Mantis Shrimp\bin"
rhDllPath = appDataPath + r"\Dynamo\0.8\packages\Mantis Shrimp\bin\Rhino3dmIO.dll"
if msPath not in sys.path:
	sys.path.Add(msPath)
if rhPath not in sys.path:
	sys.path.Add(rhPath)
	clr.AddReferenceToFileAndPath(rhDllPath)

#The inputs to this node will be stored as a list in the IN variable.
dataEnteringNode = IN
rhModel = IN[0]
rhLayer = IN[1]

objects = rhModel.Objects.FindByLayer(rhLayer)

#Assign your output to the OUT variable
OUT = objects
