"""
Copyright(c) 2015, Konrad Sobon
@arch_laboratory, http://archi-lab.net

Grasshopper and Dynamo interop library

"""
import clr
import sys
sys.path.append(r"C:\Program Files\Dynamo 0.8")
clr.AddReference('ProtoGeometry')

pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

import os
import os.path
appDataPath = os.getenv('APPDATA')
msPath = appDataPath + r"\Dynamo\0.8\packages\Mantis Shrimp\extra"
if msPath not in sys.path:
        sys.path.Add(msPath)
txtFilePath = appDataPath + r"\Dynamo\0.8\packages\Mantis Shrimp\extra\rhPath.txt"
if not os.path.isfile(txtFilePath):
	message = "Provide valid RhinoCommon.dll path."
else:
	file = open(txtFilePath, 'r+')
	rhDllPath = file.readline()
	clr.AddReferenceToFileAndPath(rhDllPath)
	file.close()

from System import *
from System.Collections.Generic import *
import Autodesk.DesignScript as ds
import Rhino as rc
import pickle

""" Misc Functions """
def process_list(_func, _list):
    return map( lambda x: process_list(_func, x) if type(x)==list else _func(x), _list )

#join/group curves function
def groupCurves(Line_List): 
	ignore_distance = 0.1
	Grouped_Lines = [] 
	Queue = set() 
	while Line_List: 
		Shape = [] 
		Queue.add(Line_List.pop())
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


""" Rhino Interop Functions """
#point/control point conversion function
def rhPointToPoint(rhPoint):
	rhPointX = rhPoint.Location.X
	rhPointY = rhPoint.Location.Y
	rhPointZ = rhPoint.Location.Z
	return ds.Geometry.Point.ByCoordinates(rhPointX, rhPointY, rhPointZ)

#3dPoint Conversion function
def rhPoint3dToPoint(rhPoint):
	rhPointX = rhPoint.X
	rhPointY = rhPoint.Y
	rhPointZ = rhPoint.Z
	return ds.Geometry.Point.ByCoordinates(rhPointX, rhPointY, rhPointZ)

#Vector3d conversion function
def rhVector3dToVector(rhVector):
	VectorX = rhVector.X
	VectorY = rhVector.Y
	VectorZ = rhVector.Z
	return ds.Geometry.Vector.ByCoordinates(VectorX, VectorY, VectorZ)

#Plane conversion function
def rhPlaneToPlane(rhPlane):
	normal = rhVector3dToVector(rhPlane.Normal)
	origin = rhPoint3dToPoint(rhPlane.Origin)
	dsPlane = ds.Geometry.Plane.ByOriginNormal(origin, normal)
	normal.Dispose()
	origin.Dispose()
	return dsPlane

#arc conversion function
def rhArcToArc(rhArc):
	dsStartPoint = rhPoint3dToPoint(rhArc.Arc.StartPoint)
	dsEndPoint = rhPoint3dToPoint(rhArc.Arc.EndPoint)
	dsCenter = rhPoint3dToPoint(rhArc.Arc.Center)
	dsArc = ds.Geometry.Arc.ByCenterPointStartPointEndPoint(dsCenter, dsStartPoint, dsEndPoint)
	dsStartPoint.Dispose()
	dsEndPoint.Dispose()
	dsCenter.Dispose()
	return dsArc

#LineCurve & Line conversion functions
def rhLineToLine(rhCurve):
	try:
		dsStartPoint = rhPoint3dToPoint(rhCurve.From)
		dsEndPoint = rhPoint3dToPoint(rhCurve.To)
	except:
		dsStartPoint = rhPoint3dToPoint(rhCurve.PointAtStart)
		dsEndPoint = rhPoint3dToPoint(rhCurve.PointAtEnd)
		pass
	return ds.Geometry.Line.ByStartPointEndPoint(dsStartPoint, dsEndPoint)

#circle conversion function
def rhCircleToCircle(rhCurve):
	rhCircle = rhCurve.TryGetCircle()[1]
	radius = rhCircle.Radius
	plane = rhPlaneToPlane(rhCircle.Plane)
	dsCircle = ds.Geometry.Circle.ByPlaneRadius(plane, radius)
	plane.Dispose()
	return dsCircle

#ellipse conversion function
def rhEllipseToEllipse(item):
	pt0 = rhPointToPoint(item.Points[0])
	pt2 = rhPointToPoint(item.Points[2])
	pt4 = rhPointToPoint(item.Points[4])
	origin = ds.Geometry.Line.ByStartPointEndPoint(pt0, pt4).PointAtParameter(0.5)
	vector1 = ds.Geometry.Vector.ByTwoPoints(origin, pt2)
	vector2 = ds.Geometry.Vector.ByTwoPoints(origin, pt4)
	ellipse = ds.Geometry.Ellipse.ByOriginVectors(origin, vector1, vector2)
	pt0.Dispose()
	pt2.Dispose()
	pt4.Dispose()
	origin.Dispose()
	vector1.Dispose()
	vector2.Dispose()
	return ellipse

#multi span nurbs curve comversion function
def rhMultiSpanNurbsCurveToCurve(rhCurve):
	dsNurbsCurve, rhSubCurve = [], []
	spanCount = rhCurve.SpanCount
	for i in range(0, spanCount, 1):
		rhCurveSubdomain = rhCurve.SpanDomain(i)
		rhSubCurve.append(rhCurve.ToNurbsCurve(rhCurveSubdomain))
	for curve in rhSubCurve:
		ptArray, weights, knots = [], [], []
		rhControlPoints = curve.Points
		for rhPoint in rhControlPoints:
			dsPoint = rhPointToPoint(rhPoint)
			ptArray.append(dsPoint)
			weights.append(rhPoint.Weight)
		ptArray = List[ds.Geometry.Point](ptArray)
		weights = Array[float](weights)
		degree = curve.Degree
		rhKnots = curve.Knots
		for i in rhKnots:
			knots.append(i)
		knots.insert(0, knots[0])
		knots.insert(len(knots), knots[(len(knots)-1)])
		knots = Array[float](knots)
		dsNurbsCurve.append(ds.Geometry.NurbsCurve.ByControlPointsWeightsKnots(ptArray, weights, knots, degree))
		curveArray = List[ds.Geometry.Curve](dsNurbsCurve)
		polyCurve = ds.Geometry.PolyCurve.ByJoinedCurves(curveArray)
		curveArray.Clear()
		ptArray.Clear()
		Array.Clear(weights, 0, len(weights))
		Array.Clear(knots, 0, len(knots))
		
	return polyCurve
	del dsNurbsCurve[:]

#single span nurbs curve conversion function
def rhSingleSpanNurbsCurveToCurve(rhCurve):		
	ptArray, weights, knots = [], [], []
	rhControlPoints = rhCurve.Points
	for rhPoint in rhControlPoints:
		dsPoint = rhPointToPoint(rhPoint)
		ptArray.append(dsPoint)
		weights.append(rhPoint.Weight)
	ptArray = List[ds.Geometry.Point](ptArray)
	weights = Array[float](weights)
	degree = rhCurve.Degree
	rhKnots = rhCurve.Knots
	for i in rhKnots:
		knots.append(i)
	knots.insert(0, knots[0])
	knots.insert(len(knots), knots[(len(knots)-1)])
	knots = Array[float](knots)
	dsNurbsCurve = ds.Geometry.NurbsCurve.ByControlPointsWeightsKnots(ptArray, weights, knots, degree)
	ptArray.Clear()
	Array.Clear(weights, 0, len(weights))
	Array.Clear(knots, 0, len(knots))
	return dsNurbsCurve

#polyline conversion function
def rhPolylineToPolyCurve(rhCurve):
	segments = rhCurve.GetSegments()
	lineArray = List[ds.Geometry.Curve]()
	for i in segments:
		lineArray.Add(rhLineToLine(i))
	dsPolyline = ds.Geometry.PolyCurve.ByJoinedCurves(lineArray)
	lineArray.Clear()
	return dsPolyline

#poly curve conversion function
def rhCurveToPolyCurve(rhCurve):
	ptArray = []
	pCount = rhCurve.PointCount
	for i in range(0, pCount):
		dsPoint = rhPoint3dToPoint(rhCurve.Point(i))
		ptArray.append(dsPoint)
	dsPolyCurve = ds.Geometry.PolyCurve.ByPoints(ptArray)
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
		elif curve.ToString() == "Rhino.Geometry.NurbsCurve" and curve.SpanCount==1:
			dsSubCurves.append(rhSingleSpanNurbsCurveToCurve(curve))
		elif curve.ToString() == "Rhino.Geometry.NurbsCurve" and curve.SpanCount > 1:
			dsSubCurves.append(rhMultiSpanNurbsCurveToCurve(curve))
		elif curve.ToString() == "Rhino.Geometry.PolyCurve":
			subPolyCurves = rhMultiSpanNurbsCurveToCurve(curve.ToNurbsCurve())
			for curve in subPolyCurves:
				dsSubCurves.append(curve)
	dsPolyCurve = ds.Geometry.PolyCurve.ByJoinedCurves(dsSubCurves)
	del dsSubCurves[:]
	return dsPolyCurve

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
	controlPointsArrayArray = Array[Array[ds.Geometry.Point]](map(tuple, newControlPoints))
	dsNurbsSurface = ds.Geometry.NurbsSurface.ByControlPointsWeightsKnots(controlPointsArrayArray, weightsArrayArray, dsKnotsU, dsKnotsV, dsDegreeU, dsDegreeV)
	return dsNurbsSurface

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
				curveArray = List[ds.Geometry.Curve](dsSubCurves)
				trimLoop.append(ds.Geometry.PolyCurve.ByJoinedCurves(curveArray))
				dsFaces.append(trimFace.TrimWithEdgeLoops(trimLoop))
				del dsSubCurves[:]
			except:
				pass
			if len(trimLoop) == 0:
				subCurveSet = set(dsSubCurves)
				del dsSubCurves[:]
				groupedCurves = groupCurves(subCurveSet)
				for i in groupedCurves:
					curveArray = List[ds.Geometry.Curve](i)
					if curveArray.Count > 1:
						trimLoops.append(ds.Geometry.PolyCurve.ByJoinedCurves(curveArray))
					else:
						trimLoops.append(curveArray[0])
				dsFaces.append(trimFace.TrimWithEdgeLoops(trimLoops))
				del trimLoops[:]
				del groupedCurves[:]
			else:
				del trimLoop[:]
	try:
		dsSurface = ds.Geometry.PolySurface.ByJoinedSurfaces(dsFaces)
	except:
		pass
	del dsFaces[:]
	return dsSurface

def rhMeshToMesh(rhMesh):
	vertexPositions, indices, indexGroups = [], [], []
	faces = rhMesh.Faces
	topologyVerticesList = rhMesh.TopologyVertices
	for i in range(0, rhMesh.Faces.Count, 1):
		indices.append(faces.GetTopologicalVertices(i))
	for i in range(0, topologyVerticesList.Count, 1):
		vertexPositions.append(rhPoint3dToPoint(topologyVerticesList.Item[i]))
	for i in indices:
		if len(i) == 3:
			a = i[0]
			b = i[1]
			c = i[2]
			indexGroups.append(ds.Geometry.IndexGroup.ByIndices(a,b,c))
		elif len(i) == 4:
			a = i[0]
			b = i[1]
			c = i[2]
			d = i[3]
			indexGroups.append(ds.Geometry.IndexGroup.ByIndices(a,b,c,d))
	dsMesh = ds.Geometry.Mesh.ByPointsFaceIndices(vertexPositions, indexGroups)
	for i in vertexPositions:
		i.Dispose()
	return dsMesh


""" Data Class """
class MSData(object):

        def __init__(self, _data = None):
                self.data = _data
        def addData(self, data):
                self.data = data

""" Geometry Classes """            
class MSVector(object):

        def __init__(self, x= None, y= None, z= None):
                self.x = x
                self.y = y
                self.z = z
        def addData(self, data):
                self.data = data
        def toDSVector(self):
                dsVector = ds.Geometry.Vector.ByCoordinates(self.x, self.y, self.z)
                return dsVector
        def toRHVector3d(self):
                rhVector = rc.Geometry.Vector3d(self.x, self.y, self.z)
                return rhVector

class MSPoint(object):

        def __init__( self, x= None, y= None, z =None):
                self.x = x
                self.y = y
                self.z = z
        def addData(self, data):
                self.data = data
        def toDSPoint(self):
                dsPoint = ds.Geometry.Point.ByCoordinates(self.x, self.y, self.z)
                return dsPoint
        def toRHPoint3d(self):
                rhPoint = rc.Geometry.Point3d(self.x, self.y, self.z)
                return rhPoint

class MSPoint4d(object):

        def __init__( self, x= None, y= None, z= None, weight= None):
                self.x = x
                self.y = y
                self.z = z
                self.weight = weight
        def addData(self, data):
                self.data = data
        def toDSPoint(self):
                dsPoint = ds.Geometry.Point.ByCoordinates(self.x, self.y, self.z)
                return dsPoint
        def toRHPoint4d(self):
                rhPoint4d = rc.Geometry.Point4d(self.x, self.y, self.z, self.weight)
                return rhPoint4d

class MSPlane(object):

        def __init__(self, origin= None, vector= None):
                self.origin = origin
                self.vector = vector
        def addData(self, data):
                self.data = data
        def toDSPlane(self):
                dsOrigin = self.origin.toDSPoint()
                dsVector = self.vector.toDSVector()
                dsPlane = ds.Geometry.Plane.ByOriginNormal(dsOrigin, dsVector)
                return dsPlane
        def toRHPlane(self):
                rhOrigin = self.origin.toRHPoint3d()
                rhVector = self.vector.toRHVector3d()
                rhPlane = rc.Geometry.Plane(rhOrigin, rhVector)
                return rhPlane

class MSLine(object):

        def __init__( self, start= None, end= None):
                self.start = start
                self.end = end
        def addData(self, data):
                self.data = data
        def toDSLine(self):
                dsStartPt = self.start.toDSPoint()
                dsEndPt = self.end.toDSPoint()
                dsLine = ds.Geometry.Line.ByStartPointEndPoint(dsStartPt, dsEndPt)
                return dsLine
        def toRHLineCurve(self):
                rhStartPt = self.start.toRHPoint3d()
                rhEndPt = self.end.toRHPoint3d()
                rhLine = rc.Geometry.LineCurve(rhStartPt, rhEndPt)
                return rhLine

class MSCircle(object):

        def __init__(self, plane= None, radius= None):
                self.plane = plane
                self.radius = radius
        def addData(self, data):
                self.data = data
        def toDSCircle(self):
                dsPlane = self.plane.toDSPlane()
                dsCircle = ds.Geometry.Circle.ByPlaneRadius(dsPlane, self.radius)
                return dsCircle
        def toRHCircle(self):
                rhPlane = self.plane.toRHPlane()
                rhCircle = rc.Geometry.Circle(rhPlane, self.radius)
                return rhCircle

class MSEllipse(object):

        def __init__(self, origin=None, ptX=None, ptY=None, plane=None, xRadius=None, yRadius=None):
                self.origin = origin
                self.ptX = ptX
                self.ptY = ptY
                self.plane = plane
                self.xRadius = xRadius
                self.yRadius = yRadius
        def addData(self, data):
                self.data = data
        def toDSEllipse(self):
                origin = self.origin.toDSPoint()
                ptX = self.ptX.toDSPoint()
                ptY = self.ptY.toDSPoint()
                vectorX = ds.Geometry.Vector.ByTwoPoints(origin, ptX)
                vectorY = ds.Geometry.Vector.ByTwoPoints(origin, ptY)
                return ds.Geometry.Ellipse.ByOriginVectors(origin, vectorX, vectorY)
        def toRHEllipse(self):
                rhOrigin = self.origin.toRHPoint3d()
                rhX = self.ptX.toRHPoint3d()
                rhY = self.ptY.toRHPoint3d()
                return rc.Geometry.Ellipse(center=rhOrigin, second=rhX, third=rhY)

class MSArc(object):

        def __init__(self, startPoint= None, centerPoint= None, endPoint= None):
                self.centerPoint = centerPoint
                self.startPoint = startPoint
                self.endPoint = endPoint
        def addData(self, data):
                self.data = data
        def toDSArc(self):
                dsStartPt = self.startPoint.toDSPoint()
                dsEndPt = self.endPoint.toDSPoint()
                dsCenterPt = self.centerPoint.toDSPoint()
                return ds.Geometry.Arc.ByCenterPointStartPointEndPoint(dsCenterPt, dsStartPt, dsEndPt)
        def toRHArc(self):
                rhStartPt = self.startPoint.toRHPoint3d()
                rhEndPt = self.endPoint.toRHPoint3d()
                rhMidPt = self.centerPoint.toRHPoint3d()
                return rc.Geometry.Arc(rhStartPt, rhMidPt, rhEndPt)

class MSPolyLine(object):

        def __init__( self, segments = None):
                self.segments = segments
        def addData(self, data):
                self.data = data
        def toDSPolyCurve(self):
                dsLines = []
                for line in self.segments:
                        dsLines.append(line.toDSLine())
                dsPolyCurve = ds.Geometry.PolyCurve.ByJoinedCurves(dsLines)
                return dsPolyCurve
        def toRHPolyCurve(self):
                rhPolyCurve = rc.Geometry.PolyCurve()
                for line in self.segments:
                        rhPolyCurve.Append(line.toRHLineCurve())
                return rhPolyCurve

class MSNurbsCurve(object):

        def __init__( self, points= None, weights= None, knots= None, degree= None):
                self.points = points
                self.weights = weights
                self.knots = knots
                self.degree = degree
        def addData(self, data):
                self.data = data
        def toDSNurbsCurve(self):
                dsPoints = []
                dsWeights = []
                for index, pt in enumerate(self.points):
                        dsPoints.append(pt.toDSPoint())
                        dsWeights.append(float(pt.weight))
                dsPtArray = Array[ds.Geometry.Point](dsPoints)
                dsWeightsArray = Array[float](dsWeights)
                dsKnots = []
                for i in self.knots:
                        dsKnots.append(i)
                dsKnots.insert(0, dsKnots[0])
                dsKnots.insert(len(dsKnots), dsKnots[(len(dsKnots)-1)])
                dsKnotsArray = Array[float](dsKnots)
                dsNurbsCurve = ds.Geometry.NurbsCurve.ByControlPointsWeightsKnots(dsPtArray, dsWeightsArray, dsKnotsArray, self.degree)
                return dsNurbsCurve
        def toRHNurbsCurve(self):
                rhNurbsCurve = rc.Geometry.NurbsCurve(int(self.degree), int(len(self.points)))
                for index, pt in enumerate(self.points):
                        rhNurbsCurve.Points.SetPoint(index, pt.toRHPoint4d())
                rhKnots = []
                for i in self.knots:
                     rhKnots.append(i)
                del rhKnots[0]
                del rhKnots[-1]
                for index, knot in enumerate(rhKnots):
                        rhNurbsCurve.Knots[index] = knot
                return rhNurbsCurve

class MSPolyCurve(object):

        def __init__(self, curves= None):
                self.curves = curves
        def addData(self, data):
                self.data = data
        def toDSPolyCurve(self):
                dsSubCurves = []
                for crv in self.curves:
                        if type(crv) == MSLine:
                                dsSubCurves.append(crv.toDSLine())
                        elif type(crv) == MSArc:
                                dsSubCurves.append(crv.toDSArc())
                        elif type(crv) == MSPolyLine:
                                dsSubCurves.append(crv.toDSPolyCurve())
                        elif type(crv) == MSNurbsCurve:
                                dsSubCurves.append(crv.toDSNurbsCurve().ToNurbsCurve())
                dsPolyCurve = ds.Geometry.PolyCurve.ByJoinedCurves(dsSubCurves)
                return dsPolyCurve
        def toRHPolyCurve(self):
                rhPolyCurve = rc.Geometry.PolyCurve()
                for j in self.curves:
                        if type(j) == MSLine:
                                rhPolyCurve.Append(j.toRHLineCurve())
                        elif type(j) == MSArc:
                                rhPolyCurve.Append(j.toRHArc())
                        elif type(j) == MSNurbsCurve:
                                rhPolyCurve.Append(j.toRHNurbsCurve())
                return rhPolyCurve

class MSMesh(object):

        def __init__(self, points = None, faceTopology = None):
                self.points = points
                self.faceTopology = faceTopology
        def addData(self, data):
                self.data = data
        def toDSMesh(self):
                dsIndexGroups = []
                for i in self.faceTopology:
                        if len(i) == 3:
                                dsIndexGroups.append(ds.Geometry.IndexGroup.ByIndices(i[0], i[1], i[2]))
                        else:
                                dsIndexGroups.append(ds.Geometry.IndexGroup.ByIndices(i[0], i[1], i[2], i[3]))
                dsVertexPositions = []
                for i in self.points:
                        dsVertexPositions.append(i.toDSPoint())
                dsMesh = ds.Geometry.Mesh.ByPointsFaceIndices(dsVertexPositions, dsIndexGroups)
                return dsMesh
        def toRHMesh(self):	
                rhMesh = rc.Geometry.Mesh()		
                for pt in self.points:		
                        rhMesh.Vertices.Add(pt.toRHPoint3d())		
                rhFaces = []
                for face in self.faceTopology:
        		if len(face)==3:
				rhMeshFace = rc.Geometry.MeshFace(face[0], face[1], face[2])
			else:
				rhMeshFace = rc.Geometry.MeshFace(face[0], face[1], face[2], face[3])
                        rhFaces.append(rhMeshFace)		
                rhFaceArray = Array[rc.Geometry.MeshFace](rhFaces)		
                rhMesh.Faces.AddFaces(rhFaceArray)		
                return rhMesh


class MSNurbsSurface(object):

        def __init__(self, points= None, weights = None, knotsU= None, knotsV= None, degreeU= None, degreeV= None, countU= None, countV= None, rational= None):
                self.points = points
                self.weights = weights
                self.knotsU = knotsU
                self.knotsV = knotsV
                self.degreeU = degreeU
                self.degreeV = degreeV
                self.countU = countU
                self.countV = countV
                self.rational = rational
        def addData(self, data):
                self.data = data
        def toDSNurbsSurface(self):
                # DS Requires Control Points to be in .Net typed arrays
                # convert Rhino Control Points to ArrayArray
                # get control points and weights 
                dsControlPoints, dsWeights = [], []
                for pt in self.points:
                        dsControlPoints.append(pt.toDSPoint())
                        dsWeights.append(pt.weight)
                # get knotsU and knotsV
                # convert list of knots to Array
                dsKnotsU, dsKnotsV = [], []
                for i in self.knotsU:
                        dsKnotsU.append(i)
                dsKnotsU.insert(0,dsKnotsU[0])
                dsKnotsU.insert(len(dsKnotsU), dsKnotsU[len(dsKnotsU)-1])
                dsKnotsU = Array[float](dsKnotsU)
                for i in self.knotsV:
                        dsKnotsV.append(i)
                dsKnotsV.insert(0, dsKnotsV[0])
                dsKnotsV.insert(len(dsKnotsV), dsKnotsV[len(dsKnotsV)-1])
                dsKnotsV = Array[float](dsKnotsV)
                # get degreeU and degreeV via Order - 1
                dsDegreeU = self.degreeU - 1
                dsDegreeV = self.degreeV - 1
                # compute number of UV Control Points
                uCount = self.countU + 3
                vCount = self.countV + 3
                #split control points into sublists of UV points
                #convert list of lists to Array[Array[point]]
                newControlPoints = [dsControlPoints[i:i+vCount] for i  in range(0, len(dsControlPoints), vCount)]
                controlPointsArrayArray = Array[Array[ds.Geometry.Point]](map(tuple, newControlPoints))
                newWeights = [dsWeights[i:i+vCount] for i  in range(0, len(dsWeights), vCount)]
                weightsArrayArray = Array[Array[float]](map(tuple, newWeights))
                # create DS NurbsSurface
                dsNurbsSurface = ds.Geometry.NurbsSurface.ByControlPointsWeightsKnots(controlPointsArrayArray, weightsArrayArray, dsKnotsU, dsKnotsV, dsDegreeU, dsDegreeV)
                return dsNurbsSurface
        def toRHNurbsSurface(self):
                # Rhino uses something called Order instead of Degree. Order = Degree + 1
                rhOrderU = self.degreeU + 1
                rhOrderV = self.degreeV + 1
                dim = 3
                # Creates internal uninitialized arrays for 
                # control points and knot
                rhNurbsSurface = rc.Geometry.NurbsSurface.Create(dim, self.rational, rhOrderU, rhOrderV, self.countU, self.countV)
                # Dynamo uses superfluous knots so first and last need to be deleted
                # number of Knots = Degree + CountU - 1
                rhKnotsU, rhKnotsV = [], []
                for i in list(self.knotsU):
                        rhKnotsU.append(i)
                del rhKnotsU[0]
                del rhKnotsU[-1]
                for i in list(self.knotsV):
                        rhKnotsV.append(i)
                del rhKnotsV[0]
                del rhKnotsV[-1]
                # add the knots
                for i in range(0, rhNurbsSurface.KnotsU.Count, 1):
                        rhNurbsSurface.KnotsU[i] = rhKnotsU[i]
                for j in range(0, rhNurbsSurface.KnotsV.Count, 1):
                        rhNurbsSurface.KnotsV[j] = rhKnotsV[j]
                # add the control points
                controlPts = [[] for i in range(len(list(self.points)))]
                for index, ptList in enumerate(self.points):
                        for pt in ptList:
                                controlPts[index].append(pt.toRHPoint4d())
                for i, _list in enumerate(controlPts):
                        for j, _item in enumerate(_list):
                              rhNurbsSurface.Points.SetControlPoint(i,j, rc.Geometry.ControlPoint(_item))
                return rhNurbsSurface

class MSMultiSpanNurbsCurve(object):

        def __init__(self, curves = None):
                self.curves = curves
        def addData(self, data):
                self.data = data
        def toDSPolyCurve(self):
                nurbsCurves = []
                for i in self.curves:
                        nurbsCurves.append(i.toDSNurbsCurve())
                dsPolyCurve = ds.Geometry.PolyCurve.ByJoinedCurves(nurbsCurves)
                return dsPolyCurve

class MSBrep(object):

        def __init__(self, faces = None, trims = None):
                self.faces = faces
                self.trims = trims
        def addData(self, data):
                self.data = data
        def toDSPolySurface(self):
                dsFaces = []
                for face, loop in zip(self.faces, self.trims):
                        dsFace = face.toDSNurbsSurface()
                        if len(loop) != 0:
                                trimLoops = []
                                for trim in loop:
                                        dsTrims = []
                                        for curve in trim:
                                                if type(curve) == MSNurbsCurve:
                                                        dsTrims.append(curve.toDSNurbsCurve())
                                                elif type(curve) == MSMultiSpanNurbsCurve:
                                                        for i in curve.curves:
                                                                dsTrims.append(i.toDSNurbsCurve())
                                                elif type(curve) == MSLine:
                                                        dsTrims.append(curve.toDSLine())
                                                elif type(curve) == MSCircle:
                                                        dsTrims.append(curve.toDSCircle())
                                                elif type(curve) == MSArc:
                                                        dsTrims.append(curve.toDSArc())
                                                elif type(curve) == MSEllipse:
                                                        dsTrims.append(curve.toDSEllipse())
                                                elif type(curve) == MSPolyCurve:
                                                        dsTrims.append(curve.toDSPolyCurve())
                                                elif type(curve) == MSPolyLine:
                                                        dsTrims.append(curve.toDSPolyCurve())
                                        curveArray = List[ds.Geometry.Curve](dsTrims)
                                        trimLoops.append(ds.Geometry.PolyCurve.ByJoinedCurves(curveArray))
                                dsFaces.append(dsFace.TrimWithEdgeLoops(trimLoops))
                        else:
                                dsFaces.append(dsFace)
                return ds.Geometry.PolySurface.ByJoinedSurfaces(dsFaces)
        def toRHBrep(self):
            rhFaces = []
            brep = rc.Geometry.Brep()
            bFaces = brep.Faces
            for i in self.faces:
                bFaces.Add(i.toRHNurbsSurface())
            return brep
