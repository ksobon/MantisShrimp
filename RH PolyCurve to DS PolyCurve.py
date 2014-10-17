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

from System import Array
from System.Collections.Generic import *

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

#point/control point conversion function
def rhPointToPoint(rhPoint):
	rhPointX = rhPoint.Location.X
	rhPointY = rhPoint.Location.Y
	rhPointZ = rhPoint.Location.Z
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

#arc conversion function
def rhArcToArc(rhArc):
	dsStartPoint = rhPoint3dToPoint(rhArc.Arc.StartPoint)
	dsEndPoint = rhPoint3dToPoint(rhArc.Arc.EndPoint)
	dsCenter = rhPoint3dToPoint(rhArc.Arc.Center)
	dsArc = Arc.ByCenterPointStartPointEndPoint(dsCenter, dsStartPoint, dsEndPoint)
	return dsArc

#single span nurbs curve conversion function
def rhSingleSpanNurbsCurveToCurve(rhCurve):		
	#get control points
	ptArray, weights, knots = [], [], []
	rhControlPoints = rhCurve.Points
	for rhPoint in rhControlPoints:
		dsPoint = rhPointToPoint(rhPoint)
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

#multi span nurbs curve comversion function
def rhMultiSpanNurbsCurveToCurve(rhCurve):
	dsNurbsCurve, rhSubCurve = [], []
	spanCount = rhCurve.SpanCount
	for i in range(0, spanCount, 1):
		rhCurveSubdomain = rhCurve.SpanDomain(i)
		rhSubCurve.append(rhCurve.ToNurbsCurve(rhCurveSubdomain))
	for curve in rhSubCurve:
		#get control points
		ptArray, weights, knots = [], [], []
		rhControlPoints = curve.Points
		for rhPoint in rhControlPoints:
			dsPoint = rhPointToPoint(rhPoint)
			ptArray.append(dsPoint)
			#get weights for each point
			weights.append(rhPoint.Weight)
		#convert Python list to IEnumerable[]
		ptArray = List[Point](ptArray)
		weights = Array[float](weights)
		#get degree of the curve
		degree = curve.Degree
		#get knots of the curve
		rhKnots = curve.Knots
		for i in rhKnots:
			knots.append(i)
		knots.insert(0, knots[0])
		knots.insert(len(knots), knots[(len(knots)-1)])
		knots = Array[float](knots)
		#create ds curve from points, weights and knots
		dsNurbsCurve.append(NurbsCurve.ByControlPointsWeightsKnots(ptArray, weights, knots, degree))
		ptArray.Clear()
		Array.Clear(weights, 0, len(weights))
		Array.Clear(knots, 0, len(knots))
	return dsNurbsCurve
	del dsNurbsCurve[:]

#poly curve conversion function
def rhCurveToPolyCurve(rhCurve):
	ptArray = []
	pCount = rhCurve.PointCount
	for i in range(0, pCount):
		dsPoint = rhPoint3dToPoint(rhCurve.Point(i))
		ptArray.append(dsPoint)
	dsPolyCurve = PolyCurve.ByPoints(ptArray)
	del ptArray[:]
	return dsPolyCurve

#rh polycurve conversion function
def rhPolyCurveToPolyCurve(rhCurve):
	dsSubCurves = []
	segmentCount = rhCurve.SegmentCount
	for i in range(0, segmentCount, 1):
		curve = rhCurve.SegmentCurve(i)
		if curve.ToString() == "Rhino.Geometry.LineCurve":
			dsSubCurves.append(rhLineToLine(curve))
		elif curve.ToString() == "Rhino.Geometry.PolylineCurve":
			dsSubCurves.append(rhCurveToPolyCurve(curve))
		elif curve.ToString() == "Rhino.Geometry.ArcCurve":
			dsSubCurves.append(rhArcToArc(curve))
		elif curve.ToString() == "Rhino.Geometry.NurbsCurve" and curve.SpanCount == 1:
			dsSubCurves.append(rhSingleSpanNurbsCurveToCurve(curve))
		elif curve.ToString() == "Rhino.Geometry.NurbsCurve" and curve.SpanCount > 1:
			multiSpanCurves = rhMultiSpanNurbsCurveToCurve(curve)
			for curve in multiSpanCurves:
				dsSubCurves.append(curve)
		elif curve.ToString() == "Rhino.Geometry.PolyCurve":
			subPolyCurves = rhMultiSpanNurbsCurveToCurve(curve.ToNurbsCurve())
			for curve in subPolyCurves:
				dsSubCurves.append(curve)
	dsPolyCurve = PolyCurve.ByJoinedCurves(dsSubCurves)
	del dsSubCurves[:]
	return dsPolyCurve

#convert to DS poly curve
dsPolyCurves = []
for i in rhObjects:
	try:
		i = i.Geometry
	except:
		pass
	if i.ToString() == "Rhino.Geometry.PolyCurve":
		dsPolyCurves.append(rhPolyCurveToPolyCurve(i))

#Assign your output to the OUT variable
OUT = dsPolyCurves
