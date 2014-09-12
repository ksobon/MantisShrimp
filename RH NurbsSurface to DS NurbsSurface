#Copyright(c) 2014, Konrad Sobon
# @arch_laboratory, http://archi-lab.net

import clr
import sys
RhinoIOPath = r'C:\Program Files\Dynamo 0.7'
if RhinoIOPath not in sys.path:
	sys.path.Add(RhinoIOPath)
clr.AddReference('ProtoGeometry')
clr.AddReferenceToFileAndPath(RhinoIOPath + r"\Rhino3dmIO.dll")
from Autodesk.DesignScript.Geometry import *
import Rhino as rc

from System import Array
from System.Collections.Generic import *

# Import RevitAPI
clr.AddReference("RevitAPI")
import Autodesk

#The inputs to this node will be stored as a list in the IN variable.
dataEnteringNode = IN
rhObjects = IN[0]

#control point conversion function
def rhControlPointToPoint(rhPoint):
	rhPointX = rhPoint.Location.X
	rhPointY = rhPoint.Location.Y
	rhPointZ = rhPoint.Location.Z
	dsControlPoint = Point.ByCoordinates(rhPointX, rhPointY, rhPointZ)
	return dsControlPoint

#check if object is a poly curve
#if true convert to DS poly curve
dsNurbsSurfaces = []
dsControlPoints = []
dsWeights = []
dsKnotsU = []
dsKnotsV = []
for object in rhObjects:
	if type(object.Geometry) == rc.Geometry.Brep:
		brepFaces = object.Geometry.Faces
		n = brepFaces.Count
		for i in range(0, n, 1):
			rhSurface = brepFaces.Item[i].UnderlyingSurface()
			#get control points and weights
			rhControlPoints = rhSurface.Points
			for point in rhControlPoints:
				dsControlPoints.append(rhControlPointToPoint(point))
				dsWeights.append(point.Weight)
			#get knotsU and knotsV
			rhKnotsU = rhSurface.KnotsU
			for i in rhKnotsU:
				dsKnotsU.append(i)
			dsKnotsU.insert(0, dsKnotsU[0])
			dsKnotsU.insert(len(dsKnotsU), dsKnotsU[len(dsKnotsU)-1])
			dsKnotsU = Array[float](dsKnotsU)
			
			rhKnotsV = rhSurface.KnotsV
			for i in rhKnotsV:
				dsKnotsV.append(i)
			dsKnotsV.insert(0, dsKnotsV[0])
			dsKnotsV.insert(len(dsKnotsV), dsKnotsV[len(dsKnotsV)-1])
			dsKnotsV = Array[float](dsKnotsV)
			#get uDegree and vDegree via order-1
			dsDegreeU = (rhSurface.OrderU) - 1 
			dsDegreeV = (rhSurface.OrderV) - 1
			#compute number of UV Control points
			uCount = rhSurface.SpanCount(0) + 3
			vCount = rhSurface.SpanCount(1) + 3
			#split control points into sublists of UV points
			#convert list of lists to Array[Array[point]]
			newControlPoints = [dsControlPoints[i:i+vCount] for i  in range(0, len(dsControlPoints), vCount)]
			newWeights = [dsWeights[i:i+vCount] for i  in range(0, len(dsWeights), vCount)]
			
			weightsArrayArray = Array[Array[float]](map(tuple, newWeights))
			controlPointsArrayArray = Array[Array[Point]](map(tuple, newControlPoints))
			
			dsNurbsSurfaces.append(NurbsSurface.ByControlPointsWeightsKnots(controlPointsArrayArray, weightsArrayArray, dsKnotsU, dsKnotsV, dsDegreeU, dsDegreeV))
			
#Assign your output to the OUT variable
OUT = dsNurbsSurfaces
