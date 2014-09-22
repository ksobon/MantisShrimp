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

#Vector3d conversion function
def rhVector3dToVector(rhVector):
	VectorX = rhVector.X 
	VectorY = rhVector.Y
	VectorZ = rhVector.Z
	dsVector = Vector.ByCoordinates(VectorX, VectorY, VectorZ)
	return dsVector

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
	
#Plane conversion function
def rhPlaneToPlane(rhPlane):
	normal = rhVector3dToVector(rhPlane.Normal)
	origin = rhPoint3dToPoint(rhPlane.Origin)
	dsPlane = Plane.ByOriginNormal(origin, normal)
	return dsPlane

#Circle is considered ArcCurve
#circle conversion function
def rhArcToArc(rhCurve):
	try:
		rhCurve = rhCurve.Geometry
	except:
		pass
	if rhCurve.TryGetCircle()[0]:
		rhCircle = rhCurve.TryGetCircle()[1]
		radius = rhCircle.Radius
		plane = rhPlaneToPlane(rhCircle.Plane)
		dsCircle = Circle.ByPlaneRadius(plane, radius)
		return dsCircle
	elif rhCurve.TryGetArc()[0]:
		rhArc = rhCurve.TryGetArc()[1]
		rhStartPoint = rhArc.StartPoint
		dsStartPoint = rhPoint3dToPoint(rhStartPoint)
		rhEndPoint = rhArc.EndPoint
		dsEndPoint = rhPoint3dToPoint(rhEndPoint)
		rhCenter = rhArc.Center
		dsCenter = rhPoint3dToPoint(rhCenter)
		dsArc = Arc.ByCenterPointStartPointEndPoint(dsCenter, dsStartPoint, dsEndPoint)
		return dsArc

#convert rhino/gh geometry to ds geometry
dsCircles = []
for i in rhObjects:
	dsCircles.append(rhArcToArc(i))

#Assign your output to the OUT variable
OUT = dsCircles
