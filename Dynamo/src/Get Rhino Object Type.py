# Copyright(c) 2015, Konrad Sobon
# @arch_laboratory, http://archi-lab.net

import clr
import sys

pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

import os

appDataPath = os.getenv('APPDATA')
rhDllPath = appDataPath + r'\Dynamo\0.8\packages\Mantis Shrimp\bin\Rhino3dmIO.dll'
clr.AddReferenceToFileAndPath(rhDllPath)

import Rhino as rc

#The inputs to this node will be stored as a list in the IN variable.
dataEnteringNode = IN

if isinstance(IN[0], list):
	rhObjects = IN[0]
else:
	rhObjects = [IN[0]]

def GetObjectType(obj):
	try:
		geo = obj.Geometry
		if geo.ToString() == "Rhino.Geometry.ArcCurve" and geo.IsArc():
			objType = "Arc"
		elif geo.ToString() == "Rhino.Geometry.NurbsCurve" and geo.IsClosed and geo.IsRational:
			objType = "Ellipse"
		elif geo.ToString() == "Rhino.Geometry.ArcCurve" and geo.IsCircle():
			objType = "Circle"
		else:
			objType = geo.ToString().split(".")[2]
	except:
		objType = "Unknown"
		pass
	return objType

def ProcessList(_func, _list):
	return map( lambda x: ProcessList(_func, x) if type(x)==list else _func(x), _list )

#extract object type
try:
	errorReport = None
	objectTypes = ProcessList(GetObjectType, rhObjects)
except:
	# if error accurs anywhere in the process catch it
	import traceback
	errorReport = traceback.format_exc()

#Assign your output to the OUT variable
if errorReport == None:
	OUT = objectTypes
else:
	OUT = errorReport
