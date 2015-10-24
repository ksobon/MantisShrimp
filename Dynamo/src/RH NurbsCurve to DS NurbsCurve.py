# Copyright(c) 2015, Konrad Sobon
# @arch_laboratory, http://archi-lab.net

import clr
import sys

pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

import os
appDataPath = os.getenv('APPDATA')
msPath = appDataPath + r'\Dynamo\0.8\packages\Mantis Shrimp\extra'
if msPath not in sys.path:
	sys.path.append(msPath)
rhDllPath = appDataPath + r'\Dynamo\0.8\packages\Mantis Shrimp\bin\Rhino3dmIO.dll'
clr.AddReferenceToFileAndPath(rhDllPath)

import Rhino as rc
from mantisshrimp import rhSingleSpanNurbsCurveToCurve

#The inputs to this node will be stored as a list in the IN variable.
dataEnteringNode = IN

if isinstance(IN[0], list):
	rhObjects = IN[0]
else:
	rhObjects = [IN[0]]

def GetNurbsCurve(rhObj):
	try:
		geo = rhObj.Geometry
		if geo.ToString() == "Rhino.Geometry.NurbsCurve":
			return rhSingleSpanNurbsCurveToCurve(geo)
	except:
		pass

def ProcessList(_func, _list):
	return map(lambda x: ProcessList(_func, x) if type(x) == list else _func(x) , _list)

#convert rhino/gh geometry to ds geometry
try:
	errorReport = None
	dsNurbsCurves = ProcessList(GetNurbsCurve, rhObjects)
except:
	# if error accurs anywhere in the process catch it
	import traceback
	errorReport = traceback.format_exc()
	
#Assign your output to the OUT variable
if errorReport == None:
	OUT = dsNurbsCurves
else:
	OUT = errorReport
