#Copyright(c) 2015, Konrad Sobon
# @arch_laboratory, http://archi-lab.net

import clr
import sys
clr.AddReference('ProtoGeometry')

pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

import os
appDataPath = os.getenv('APPDATA')
msPath = appDataPath + r'\Dynamo\0.8\packages\Mantis Shrimp\extra'
if msPath not in sys.path:
	sys.path.append(msPath)
rhDllPath = appDataPath + r'\Dynamo\0.8\packages\Mantis Shrimp\bin\Rhino3dmIO.dll'
clr.AddReferenceToFileAndPath(rhDllPath)

from Autodesk.DesignScript.Geometry import *
import Rhino as rc

#The inputs to this node will be stored as a list in the IN variable.
dataEnteringNode = IN
rhObjects = IN[0]

#3dPoint Conversion function
def rhPoint3dToPoint(rhPoint):
	rhPointX = rhPoint.X
	rhPointY = rhPoint.Y
	rhPointZ = rhPoint.Z
	return Point.ByCoordinates(rhPointX, rhPointY, rhPointZ)

#LineCurve conversion function
def rhLineToLine(rhCurve):
	dsStartPoint = rhPoint3dToPoint(rhCurve.PointAtStart)
	dsEndPoint = rhPoint3dToPoint(rhCurve.PointAtEnd)
	dsLine = Line.ByStartPointEndPoint(dsStartPoint, dsEndPoint)
	dsStartPoint.Dispose()
	dsEndPoint.Dispose()
	return dsLine

#convert rhino/gh geometry to ds geometry
try:
	errorReport = None
	dsLines = []
	for i in rhObjects:
		try:
			i = i.Geometry
		except:
			pass
		if i.ToString() == "Rhino.Geometry.LineCurve":
			dsLines.append(rhLineToLine(i))
except:
	# if error accurs anywhere in the process catch it
	import traceback
	errorReport = traceback.format_exc()
	
#Assign your output to the OUT variable
if errorReport == None:
	OUT = dsLines
else:
	OUT = errorReport
