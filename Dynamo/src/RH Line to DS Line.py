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

#The inputs to this node will be stored as a list in the IN variable.
dataEnteringNode = IN
rhObjects = IN[0]
_units = IN[1]

def toDSUnits(_units):
	if _units == rc.UnitSystem.Millimeters:
		return 0.001
	elif _units == rc.UnitSystem.Centimeters:
		return 0.01
	elif _units == rc.UnitSystem.Decimeters:
		return 0.1
	elif _units == rc.UnitSystem.Meters:
		return 1
	elif _units == rc.UnitSystem.Inches:
		return 0.0254
	elif _units == rc.UnitSystem.Feet:
		return 0.3048
	elif _units == rc.UnitSystem.Yards:
		return 0.9144

#3dPoint Conversion function
def rhPoint3dToPoint(rhPoint):
	rhPointX = rhPoint.X * toDSUnits(_units)
	rhPointY = rhPoint.Y * toDSUnits(_units)
	rhPointZ = rhPoint.Z * toDSUnits(_units)
	dsPoint = Point.ByCoordinates(rhPointX, rhPointY, rhPointZ)
	return dsPoint

#LineCurve conversion function
def rhLineToLine(rhCurve):
	rhStartPoint = rhCurve.PointAtStart
	dsStartPoint = rhPoint3dToPoint(rhStartPoint)
	rhEndPoint = rhCurve.PointAtEnd
	dsEndPoint = rhPoint3dToPoint(rhEndPoint)
	dsLine = Line.ByStartPointEndPoint(dsStartPoint, dsEndPoint)
	return dsLine

#convert rhino/gh geometry to ds geometry
dsLines = []
for i in rhObjects:
	try:
		i = i.Geometry
	except:
		pass
	if i.ToString() == "Rhino.Geometry.LineCurve":
		dsLines.append(rhLineToLine(i))

#Assign your output to the OUT variable
OUT = dsLines
