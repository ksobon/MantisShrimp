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

from Autodesk.DesignScript.Geometry import *
import Rhino as rc

#The inputs to this node will be stored as a list in the IN variable.
dataEnteringNode = IN
rhObjects = IN[0]

#3dPoint Conversion
def rhPoint3dToPoint(rhPoint):
	try:
		rhPoint = rhPoint.Geometry
	except:
		pass
	rhPointX = rhPoint.X
	rhPointY = rhPoint.Y
	rhPointZ = rhPoint.Z
	dsPoint = Point.ByCoordinates(rhPointX, rhPointY, rhPointZ)
	return dsPoint

#LineCurve conversion function
def rhLineToLine(rhCurve):
	try:
		rhCurve = rhCurve.Geometry
	except:
		pass
	rhStartPoint = rhCurve.PointAtStart
	dsStartPoint = rhPoint3dToPoint(rhStartPoint)
	rhEndPoint = rhCurve.PointAtEnd
	dsEndPoint = rhPoint3dToPoint(rhEndPoint)
	dsLine = Line.ByStartPointEndPoint(dsStartPoint, dsEndPoint)
	return dsLine

#convert rhino/gh geometry to ds geometry
dsLines = []
for i in rhObjects:
	dsLines.append(rhLineToLine(i))

#Assign your output to the OUT variable
OUT = dsLines
