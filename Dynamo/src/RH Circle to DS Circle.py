#Copyright(c) 2015, Konrad Sobon
# @arch_laboratory, http://archi-lab.net

import clr
import sys
clr.AddReference('ProtoGeometry')

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

#3dPoint Conversion function
def rhPoint3dToPoint(rhPoint):
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

#circle conversion function
def rhCircleToCircle(rhCurve):
	rhCircle = rhCurve.TryGetCircle()[1]
	radius = rhCircle.Radius
	plane = rhPlaneToPlane(rhCircle.Plane)
	dsCircle = Circle.ByPlaneRadius(plane, radius)
	return dsCircle

#convert rhino/gh geometry to ds geometry
dsCircles = []
for i in rhObjects:
	try:
		i = i.Geometry
	except:
		pass
	if i.ToString() == "Rhino.Geometry.ArcCurve" and i.IsCircle():
		dsCircles.append(rhCircleToCircle(i))

#Assign your output to the OUT variable
OUT = dsCircles
