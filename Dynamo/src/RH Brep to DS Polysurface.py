#Copyright(c) 2015, Konrad Sobon
# @arch_laboratory, http://archi-lab.net

import clr
import sys
clr.AddReference('ProtoGeometry')

pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

import os
appDataPath = os.getenv('APPDATA')
msPath = appDataPath + r"\Dynamo\0.7\packages\Mantis Shrimp\extra"
rhPath = appDataPath + r"\Dynamo\0.7\packages\Mantis Shrimp\bin"
rhDllPath = appDataPath + r"\Dynamo\0.7\packages\Mantis Shrimp\bin\Rhino3dmIO.dll"
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
_units = IN[1]

#unit conversion function from Rhino to DS
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

#Vector3d conversion function
def rhVector3dToVector(rhVector):
	VectorX = rhVector.X * toDSUnits(_units)
	VectorY = rhVector.Y * toDSUnits(_units)
	VectorZ = rhVector.Z * toDSUnits(_units)
	return Vector.ByCoordinates(VectorX, VectorY, VectorZ)

#3dPoint Conversion function
def rhPoint3dToPoint(rhPoint):
	rhPointX = rhPoint.X * toDSUnits(_units)
	rhPointY = rhPoint.Y * toDSUnits(_units)
	rhPointZ = rhPoint.Z * toDSUnits(_units)
	return Point.ByCoordinates(rhPointX, rhPointY, rhPointZ)

#point/control point conversion function
def rhPointToPoint(rhPoint):
	rhPointX = rhPoint.Location.X * toDSUnits(_units)
	rhPointY = rhPoint.Location.Y * toDSUnits(_units)
	rhPointZ = rhPoint.Location.Z * toDSUnits(_units)
	return Point.ByCoordinates(rhPointX, rhPointY, rhPointZ)

#Plane conversion function
def rhPlaneToPlane(rhPlane):
	normal = rhVector3dToVector(rhPlane.Normal)
	origin = rhPoint3dToPoint(rhPlane.Origin)
	return Plane.ByOriginNormal(origin, normal)

#LineCurve conversion function
def rhLineToLine(rhCurve):
	try:
		dsStartPoint = rhPoint3dToPoint(rhCurve.From)
		dsEndPoint = rhPoint3dToPoint(rhCurve.To)
	except:
		dsStartPoint = rhPoint3dToPoint(rhCurve.PointAtStart)
		dsEndPoint = rhPoint3dToPoint(rhCurve.PointAtEnd)
		pass
	return Line.ByStartPointEndPoint(dsStartPoint, dsEndPoint)

#LineCurve conversion function
def rhLineCurveToLine(rhCurve):
	dsStartPoint = rhPoint3dToPoint(rhCurve.PointAtStart)
	dsEndPoint = rhPoint3dToPoint(rhCurve.PointAtEnd)
	return Line.ByStartPointEndPoint(dsStartPoint, dsEndPoint)

#arc conversion function
def rhArcToArc(rhArc):
	dsStartPoint = rhPoint3dToPoint(rhArc.StartPoint)
	dsEndPoint = rhPoint3dToPoint(rhArc.EndPoint)
	dsCenter = rhPoint3dToPoint(rhArc.Center)
	return Arc.ByCenterPointStartPointEndPoint(dsCenter, dsStartPoint, dsEndPoint)

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
		curveArray = List[Curve](dsNurbsCurve)
		polyCurve = PolyCurve.ByJoinedCurves(curveArray)
		curveArray.Clear()
		ptArray.Clear()
		Array.Clear(weights, 0, len(weights))
		Array.Clear(knots, 0, len(knots))
		
	return polyCurve
	del dsNurbsCurve[:]

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

#polyline conversion function
def rhPolylineToPolyCurve(rhCurve):
	segments = rhCurve.GetSegments()
	lineArray = List[Curve]()
	for i in segments:
		if i.ToString() == "Rhino.Geometry.LineCurve":
			lineArray.Add(rhLineCurveToLine(i))
		else:
			lineArray.Add(rhLineToLine(i))
	dsPolyline = PolyCurve.ByJoinedCurves(lineArray)
	lineArray.Clear()
	return dsPolyline

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

#brep/nurbs surface conversion function
def rhNurbsSurfaceToSurface(rhNurbsSurface):
	dsNurbsSurfaces = []
	dsControlPoints = []
	dsWeights = []
	#get control points and weights
	rhControlPoints = rhNurbsSurface.Points
	for point in rhControlPoints:
		dsControlPoints.append(rhPointToPoint(point))
		dsWeights.append(point.Weight)
	#get knotsU and knotsV
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
	#get uDegree and vDegree via order-1
	dsDegreeU = (rhNurbsSurface.OrderU) - 1 
	dsDegreeV = (rhNurbsSurface.OrderV) - 1
	#compute number of UV Control points
	uCount = rhNurbsSurface.SpanCount(0) + 3
	vCount = rhNurbsSurface.SpanCount(1) + 3
	#split control points into sublists of UV points
	#convert list of lists to Array[Array[point]]
	newControlPoints = [dsControlPoints[i:i+vCount] for i  in range(0, len(dsControlPoints), vCount)]
	newWeights = [dsWeights[i:i+vCount] for i  in range(0, len(dsWeights), vCount)]

	weightsArrayArray = Array[Array[float]](map(tuple, newWeights))
	controlPointsArrayArray = Array[Array[Point]](map(tuple, newControlPoints))
	#create ds nurbs surface
	dsNurbsSurface = NurbsSurface.ByControlPointsWeightsKnots(controlPointsArrayArray, weightsArrayArray, dsKnotsU, dsKnotsV, dsDegreeU, dsDegreeV)
	return dsNurbsSurface

#join/group curves function
def groupCurves(Line_List): 
	ignore_distance = 0.1 # Assume points this close or closer to each other are touching 
	Grouped_Lines = [] 
	Queue = set() 
	while Line_List: 
		Shape = [] 
		Queue.add(Line_List.pop()) # Move a line from the Line_List to our queue 
		while Queue: 
			Current_Line = Queue.pop() 
			Shape.append(Current_Line) 
			for Potential_Match in Line_List: 
				Points = (Potential_Match.StartPoint, Potential_Match.EndPoint)
				for P1 in Points: 
					for P2 in (Current_Line.StartPoint, Current_Line.EndPoint): 
						distance = P1.DistanceTo(P2) 
						if distance <= ignore_distance: 
							Queue.add(Potential_Match) 
			Line_List = [item for item in Line_List if item not in Queue]
		Grouped_Lines.append(Shape) 
	return Grouped_Lines

#brep conversion function
def rhBrepToPolySurface(brep):
	dsSubCurves, faceIndicies, trimLoops, dsFaces, trimLoop  = [], [], [], [], []
	faces = brep.Faces
	for face in faces:
		if face.IsSurface:
			dsFaces.append(rhNurbsSurfaceToSurface(face.ToNurbsSurface()))
		else:
			trimFace = rhNurbsSurfaceToSurface(face.UnderlyingSurface().ToNurbsSurface())
			faceLoops = face.Loops
			for loop in faceLoops:
				trims = loop.Trims
				for trim in trims:
					if trim.TrimType != rc.Geometry.BrepTrimType.Seam:
						edgeIndex = trim.Edge.EdgeIndex
						edge = brep.Edges.Item[edgeIndex]
						if edge.ObjectType.ToString() == "Curve" and edge.SpanCount > 1:
							dsSubCurves.append(rhMultiSpanNurbsCurveToCurve(edge))
						elif edge.ObjectType.ToString() == "Curve" and edge.SpanCount == 1:
							if edge.IsArc():
								arc = edge.TryGetArc()
								dsSubCurves.append(rhArcToArc(arc[1]))
							elif edge.IsPolyline():
								polyline = edge.TryGetPolyline()
								dsSubCurves.append(rhPolylineToPolyCurve(polyline[1]))
							else:
								dsSubCurves.append(rhSingleSpanNurbsCurveToCurve(edge.ToNurbsCurve()))	
			try:
				curveArray = List[Curve](dsSubCurves)
				trimLoop.append(PolyCurve.ByJoinedCurves(curveArray))
				dsFaces.append(trimFace.TrimWithEdgeLoops(trimLoop))
				del dsSubCurves[:]
			except:
				pass
			if len(trimLoop) == 0:
				subCurveSet = set(dsSubCurves)
				del dsSubCurves[:]
				groupedCurves = groupCurves(subCurveSet)
				for i in groupedCurves:
					curveArray = List[Curve](i)
					if curveArray.Count > 1:
						trimLoops.append(PolyCurve.ByJoinedCurves(curveArray))
					else:
						trimLoops.append(curveArray[0])
				dsFaces.append(trimFace.TrimWithEdgeLoops(trimLoops))
				del trimLoops[:]
				del groupedCurves[:]
			else:
				del trimLoop[:]
	try:
		dsSurface = PolySurface.ByJoinedSurfaces(dsFaces)
	except:
		pass
	del dsFaces[:]
	return dsSurface

#convert rhino/gh geometry to ds geometry
dsSurfaces = []
for i in rhObjects:
	try:
		i = i.Geometry
	except:
		pass
	if i.ToString() == "Rhino.Geometry.Brep":
		dsSurfaces.append(rhBrepToPolySurface(i))

OUT = dsSurfaces
