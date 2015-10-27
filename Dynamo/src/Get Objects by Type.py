# Copyright(c) 2015, Konrad Sobon
# @arch_laboratory, http://archi-lab.net

import clr
import sys

pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

import os
appDataPath = os.getenv('APPDATA')
dynVersions = ["0.7", "0.8", "0.9"]
dynFolders = ["extra", "bin"]
for i in dynVersions:
	for j in dynFolders:
		part1 = "\\Dynamo\\"
		version = i
		part2 = "\\packages\\Mantis Shrimp\\"
		folder = j
		msPath = appDataPath + part1 + version + part2 + folder
		if j == "extra":
			if msPath not in sys.path:
				sys.path.Add(msPath)
		if j == "bin":
			dllName = "\\Rhino3dmIO.dll"
			rhDllPath = appDataPath + part1 + version + part2 + folder + dllName
			if msPath not in sys.path:
				sys.path.Add(msPath)
				if os.path.isfile(rhDllPath):
					clr.AddReferenceToFileAndPath(rhDllPath)

pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

#The inputs to this node will be stored as a list in the IN variable.
dataEnteringNode = IN
rhModel = IN[0]

if isinstance(IN[1], list):
	rhType = IN[1]
else:
	rhType = [IN[1]]

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

def GetObjectsByType(rhObj = None, rht = rhType):
	if GetObjectType(rhObj) in rhType:
		return rhObj
	else:
		return None

def ClearList(_list):
    out = []
    for _list1 in _list:
        if _list1 is None:
            continue
        if not _list1:
        	continue
        if isinstance(_list1, list):
             _list1 = ClearList(_list1)
             if not _list1:
                 continue
        out.append(_list1)
    return out

def ProcessList(_func, _list):
    return map( lambda x: ProcessList(_func, x) if type(x)==list else _func(x), _list )

try:
	errorReport = None
	allObjects = rhModel.Objects
	objects = ProcessList(GetObjectsByType, allObjects)
except:
	# if error accurs anywhere in the process catch it
	import traceback
	errorReport = traceback.format_exc()

#Assign your output to the OUT variable
if errorReport == None:
	OUT = ClearList(objects)
else:
	OUT = errorReport
