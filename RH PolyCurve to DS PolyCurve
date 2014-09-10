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

#Vector3d conversion function
def rhVector3dToVector(rhVector):
	VectorX = rhVector.X 
	VectorY = rhVector.Y
	VectorZ = rhVector.Z
	dsVector = Vector.ByCoordinates(VectorX, VectorY, VectorZ)
	return dsVector

#3dPoint Conversion
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

#LineCurve conversion function
def rhLineToLine(rhCurve):
	rhStartPoint = rhCurve.PointAtStart
	dsStartPoint = rhPoint3dToPoint(rhStartPoint)
	rhEndPoint = rhCurve.PointAtEnd
	dsEndPoint = rhPoint3dToPoint(rhEndPoint)
	dsLine = Line.ByStartPointEndPoint(dsStartPoint, dsEndPoint)
	return dsLine

#ArcCurve conversion function
#Circle is considered ArcCurve so will be processed here
def rhArcToArc(rhCurve):
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

#NurbsCurve conversion function
#Ellipse is considered NurbsCurve so it will be processed here
def rhCurveToNurbsCurve(rhCurve):
	if rhCurve.HasNurbsForm() == float(1):
		rhCurve = rhCurve.ToNurbsCurve()
		#get control points
		ptArray, weights = [], []
		knots = []
		rhControlPoints = rhCurve.Points
		for rhPoint in rhControlPoints:
			rhPointX = rhPoint.Location.X
			rhPointY = rhPoint.Location.Y
			rhPointZ = rhPoint.Location.Z
			dsPoint = Point.ByCoordinates(rhPointX, rhPointY, rhPointZ)
			ptArray.append(dsPoint)
			#get weights for each point
			weights.append(rhPoint.Weight)
		#convert Python list to IEnumerable[]
		ptArray = List[Point](ptArray)
		weights = Array[float](weights)
		#get degree of the curve
		degree = rhCurve.Degree
		#get knots of the curve
		rhKnots = rhCurve.Knots
		for i in rhKnots:
			knots.append(i)
		knots.insert(0, knots[0])
		knots.insert(len(knots), knots[(len(knots)-1)])
		knots = Array[float](knots)
		#create ds curve from points, weights and knots
		dsNurbsCurve = NurbsCurve.ByControlPointsWeightsKnots(ptArray, weights, knots, degree)
		ptArray.Clear()
		Array.Clear(weights, 0, len(weights))
		Array.Clear(knots, 0, len(knots))
		return dsNurbsCurve
	
#poly curve conversion function
def rhCurveToPolyCurve(rhCurve):
	ptArray = []
	pCount = rhCurve.PointCount
	for i in range(0, pCount):
		dsPoint = rhPoint3dToPoint(rhCurve.Point(i))
		ptArray.append(dsPoint)
	dsPolyCurve = PolyCurve.ByPoints(ptArray)
	ptArray = []
	return dsPolyCurve

#check if object is a poly curve
#if true convert to DS poly curve
dsPolyCurves = []
dsSubCurves = []
for object in rhObjects:
	if type(object.Geometry) == rc.Geometry.PolyCurve:
		subCurves = object.Geometry.Explode()
		for curve in subCurves:
			if type(curve) == rc.Geometry.NurbsCurve:
				dsSubCurves.append(rhCurveToNurbsCurve(curve))
			elif type(curve) == rc.Geometry.PolylineCurve:
				dsSubCurves.append(rhCurveToPolyCurve(curve))
			elif type(curve) == rc.Geometry.LineCurve:
				dsSubCurves.append(rhLineToLine(curve))
			elif type(curve) == rc.Geometry.ArcCurve:
				dsSubCurves.append(rhArcToArc(curve))
		dsPolyCurves.append(PolyCurve.ByJoinedCurves(dsSubCurves))
		dsSubCurves = []
#Assign your output to the OUT variable
OUT = dsPolyCurves
