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
from System import Array
from System.Collections.Generic import *

#The inputs to this node will be stored as a list in the IN variable.
dataEnteringNode = IN
rhObjects = IN[0]

#point/control point conversion function
def rhPointToPoint(rhPoint):
	rhPointX = rhPoint.Location.X
	rhPointY = rhPoint.Location.Y
	rhPointZ = rhPoint.Location.Z
	return Point.ByCoordinates(rhPointX, rhPointY, rhPointZ)

#brep/nurbs surface conversion function
def rhNurbsSurfaceToSurface(rhNurbsSurface):
	dsNurbsSurfaces = []
	dsControlPoints = []
	dsWeights = []
	rhControlPoints = rhNurbsSurface.Points
	for point in rhControlPoints:
		dsControlPoints.append(rhPointToPoint(point))
		dsWeights.append(point.Weight)
	rhKnotsU = rhNurbsSurface.KnotsU
	dsKnotsU = []
	for i in rhKnotsU:
		dsKnotsU.append(i)
	dsKnotsU.insert(0, dsKnotsU[0])
	dsKnotsU.insert(len(dsKnotsU), dsKnotsU[len(dsKnotsU)-1])
	dsKnotsU = Array[float](dsKnotsU)
	rhKnotsV = rhNurbsSurface.KnotsV
	dsKnotsV = []
	for i in rhKnotsV:
		dsKnotsV.append(i)
	dsKnotsV.insert(0, dsKnotsV[0])
	dsKnotsV.insert(len(dsKnotsV), dsKnotsV[len(dsKnotsV)-1])
	dsKnotsV = Array[float](dsKnotsV)
	dsDegreeU = (rhNurbsSurface.OrderU) - 1 
	dsDegreeV = (rhNurbsSurface.OrderV) - 1
	uCount = rhNurbsSurface.SpanCount(0) + 3
	vCount = rhNurbsSurface.SpanCount(1) + 3
	newControlPoints = [dsControlPoints[i:i+vCount] for i  in range(0, len(dsControlPoints), vCount)]
	newWeights = [dsWeights[i:i+vCount] for i  in range(0, len(dsWeights), vCount)]
	weightsArrayArray = Array[Array[float]](map(tuple, newWeights))
	controlPointsArrayArray = Array[Array[Point]](map(tuple, newControlPoints))
	dsNurbsSurface = NurbsSurface.ByControlPointsWeightsKnots(controlPointsArrayArray, weightsArrayArray, dsKnotsU, dsKnotsV, dsDegreeU, dsDegreeV)
	return dsNurbsSurface

#convert nurbs surfaces to ds nurbs surfaces
dsNurbsSurfaces = []
for i in rhObjects:
	try:
		i = i.Geometry
	except:
		pass	
	if i.ToString() == "Rhino.Geometry.Brep":
		brepFaces = i.Faces
		n = brepFaces.Count
		for i in range(0, n, 1):
			rhSurface = brepFaces.Item[i].UnderlyingSurface()
			if rhSurface.ToString() == "Rhino.Geometry.NurbsSurface":
				dsNurbsSurfaces.append(rhNurbsSurfaceToSurface(rhSurface))
			
#Assign your output to the OUT variable
OUT = dsNurbsSurfaces
