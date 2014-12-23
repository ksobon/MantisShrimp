#Copyright(c) 2014, Konrad Sobon
# @arch_laboratory, http://archi-lab.net

import clr
import sys
clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *

# Import DocumentManager and TransactionManager
clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

# Import RevitAPI
clr.AddReference("RevitAPI")
import Autodesk
from Autodesk.Revit.DB import *

doc = DocumentManager.Instance.CurrentDBDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application

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
_units = IN[1]
_fillRegionId = IN[2]

def process_list(_func, _list):
	return map( lambda x: process_list(_func, x) if type(x)==list else _func(x), _list )

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
	dsVector = Vector.ByCoordinates(VectorX, VectorY, VectorZ)
	return dsVector

#3dPoint Conversion function
def rhPoint3dToPoint(rhPoint):
	rhPointX = rhPoint.X * toDSUnits(_units)
	rhPointY = rhPoint.Y * toDSUnits(_units)
	rhPointZ = rhPoint.Z * toDSUnits(_units)
	dsPoint = Point.ByCoordinates(rhPointX, rhPointY, rhPointZ)
	return dsPoint

#point/control point conversion function
def rhPointToPoint(rhPoint):
	rhPointX = rhPoint.Location.X * toDSUnits(_units)
	rhPointY = rhPoint.Location.Y * toDSUnits(_units)
	rhPointZ = rhPoint.Location.Z * toDSUnits(_units)
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

def rhCurvesToCurves(curve):
	if curve.ToString() == "Rhino.Geometry.LineCurve":
		return rhLineToLine(curve)
	elif curve.ToString() == "Rhino.Geometry.PolylineCurve":
		return rhCurveToPolyCurve(curve)
	elif curve.ToString() == "Rhino.Geometry.ArcCurve":
		return rhArcToArc(curve)
	elif curve.ToString() == "Rhino.Geometry.NurbsCurve" and curve.SpanCount == 1:
		return rhSingleSpanNurbsCurveToCurve(curve)
	elif curve.ToString() == "Rhino.Geometry.NurbsCurve" and curve.SpanCount > 1:
		return rhMultiSpanNurbsCurveToCurve(curve)
	elif curve.ToString() == "Rhino.Geometry.PolyCurve":
		return rhMultiSpanNurbsCurveToCurve(curve.ToNurbsCurve())

def toRvtPoint(point):
	unitsFactor = 3.28084 #Revit works in Feet while Dynamo in Meters
	x = point.X * unitsFactor
	y = point.Y * unitsFactor
	z = point.Z * unitsFactor
	return XYZ(x,y,z)
	
def toRvtType(dsObject):
	if type(dsObject) == NurbsCurve and dsObject.Degree >= 3:
		controlPoints = List[XYZ]()
		for pt in dsObject.ControlPoints():
			controlPoints.Add(toRvtPoint(pt))
		weights = List[float]()
		for w in dsObject.Weights():
			weights.Add(float(w))
		knots = List[float]()
		for k in dsObject.Knots():
			knots.Add(float(k))
		degree = dsObject.Degree
		closed = dsObject.IsClosed
		rational = dsObject.IsRational
		return Autodesk.Revit.DB.NurbSpline.Create(controlPoints, weights, knots, degree, closed, rational)
	elif type(dsObject) == NurbsCurve and dsObject.Degree < 3:
		points = []
		subCurves = dsObject.DivideEqually(15)
		for i in subCurves:
			points.append(i.StartPoint)
		points.insert(len(points), subCurves[(len(subCurves)-1)].EndPoint)
		controlPoints = List[XYZ]()
		for i in points:
			controlPoints.Add(toRvtPoint(i))
		return Autodesk.Revit.DB.HermiteSpline.Create(controlPoints, False)	
	elif type(dsObject) == Arc:
		#convert DS Arc to Revit Arc
		startPt = toRvtPoint(dsObject.StartPoint)
		endPt = toRvtPoint(dsObject.EndPoint)
		midPt = toRvtPoint(dsObject.PointAtParameter(0.5))
		return Autodesk.Revit.DB.Arc.Create(startPt, endPt, midPt)
	elif type(dsObject) == Line:
		#convert DS Line to Revit Line
		startPt = toRvtPoint(dsObject.StartPoint)
		endPt = toRvtPoint(dsObject.EndPoint)
		return Autodesk.Revit.DB.Line.CreateBound(startPt, endPt)
	else:
		return dsObject.ToRevitType()

def makeRvtDetailLines(crv):
	detailLine = doc.Create.NewDetailCurve(doc.ActiveView, crv)
	return detailLine

def toRvtId(_id):
	if isinstance(_id, int) or isinstance(_id, str):
		id = ElementId(int(_id))
		return id
	elif isinstance(_id, ElementId):
		return _id


#"Start" the transaction
TransactionManager.Instance.EnsureInTransaction(doc)

#convert rhino/gh geometry to ds geometry
outerCurves = [[] for i in range(len(rhObjects))]
otherCurves = []
for index, i in enumerate(rhObjects):
	try:
		i = i.Geometry
	except:
		pass
	if i.ToString() == "Rhino.Geometry.Hatch":
		outerBoundary = i.Get3dCurves(True)
		innerBoundary = i.Get3dCurves(False)
		for crv in outerBoundary:
			outerCurves[index].append(rhCurvesToCurves(crv))
		for crv in innerBoundary:
			outerCurves[index].append(rhCurvesToCurves(crv))
		rvtElements = process_list(toRvtType, outerCurves)
		for _list in rvtElements:
			profileLoops = List[CurveLoop]()
			profileLoop = CurveLoop()
			for subList in _list:
				profileLoop.Append(subList)
			profileLoops.Add(profileLoop)
			filledRegion = FilledRegion.Create(doc, toRvtId(_fillRegionId[0]), doc.ActiveView.Id, profileLoops)
			profileLoops.Clear()
	else:
		otherCurves.append(rhCurvesToCurves(i))
	rvtElements = process_list(toRvtType, otherCurves)
		rvtElements = process_list(makeRvtDetailLines, rvtElements)

# "End" the transaction
TransactionManager.Instance.TransactionTaskDone()

"""
rvtElements = process_list(toRvtType, outerCurves)

#"Start" the transaction
TransactionManager.Instance.EnsureInTransaction(doc)


for _list in rvtElements:
	profileLoops = List[CurveLoop]()
	profileLoop = CurveLoop()
	for subList in _list:
		profileLoop.Append(subList)
	profileLoops.Add(profileLoop)
	filledRegion = FilledRegion.Create(doc, toRvtId(_fillRegionId[0]), doc.ActiveView.Id, profileLoops)
	profileLoops.Clear()
	
# "End" the transaction
TransactionManager.Instance.TransactionTaskDone()
"""
#rvtElements = process_list(makeRvtDetailLines, rvtElements)
#Assign your output to the OUT variable
OUT = rvtElements
