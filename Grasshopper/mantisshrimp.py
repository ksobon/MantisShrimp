"""
Copyright(c) 2014, Konrad Sobon
@arch_laboratory, http://archi-lab.net

Grasshopper and Dynamo interop library

"""
import clr
import sys
sys.path.append(r"C:\Program Files\Dynamo 0.7")
clr.AddReference('ProtoGeometry')

pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

import os
appDataPath = os.getenv('APPDATA')
msPath = appDataPath + r"\Dynamo\0.7\packages\Mantis Shrimp\extra"
if msPath not in sys.path:
	sys.path.Add(msPath)

possibleRhPaths, message = [], None
possibleRhPaths.append(r"C:\Program Files\Rhinoceros 5 (64-bit)\System\RhinoCommon.dll")
possibleRhPaths.append(r"C:\Program Files\Rhinoceros 5.0 (64-bit)\System\RhinoCommon.dll")
possibleRhPaths.append(r"C:\Program Files\McNeel\Rhinoceros 5.0\System\RhinoCommon.dll")
possibleRhPaths.append(msPath)
checkPaths = map(lambda x: os.path.exists(x), possibleRhPaths)
for i, j in zip(possibleRhPaths, checkPaths):
	if j and i not in sys.path:
		sys.path.Add(i)
		clr.AddReferenceToFileAndPath(i)
		break
	else:
		message = "Please provide a valid path to RhinoCommon.dll"

from System import *
from System.Collections.Generic import *
import Autodesk.DesignScript as ds
import Rhino as rc
import pickle

""" Misc Functions """
def process_list(_func, _list):
    return map( lambda x: process_list(_func, x) if type(x)==list else _func(x), _list )

#unit conversion function from Rhino to DS
def toDSUnits(_units):
	if _units == "Millimeters":
		return 0.001
	elif _units == "Centimeters":
		return 0.01
	elif _units == "Decimeters":
		return 0.1
	elif _units == "Meters":
		return 1
	elif _units == "Inches":
		return 0.0254
	elif _units == "Feet":
		return 0.3048
	elif _units == "Yards":
		return 0.9144

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
        def toDSVector(self, units):
                dsVector = ds.Geometry.Vector.ByCoordinates(self.x * toDSUnits(units), self.y * toDSUnits(units), self.z * toDSUnits(units))
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
        def toDSPoint(self, units):
                dsPoint = ds.Geometry.Point.ByCoordinates(self.x * toDSUnits(units), self.y * toDSUnits(units), self.z * toDSUnits(units))
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
        def toDSPoint(self, units):
                dsPoint = ds.Geometry.Point.ByCoordinates(self.x * toDSUnits(units), self.y * toDSUnits(units), self.z * toDSUnits(units))
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
        def toDSPlane(self, units):
                dsOrigin = self.origin.toDSPoint(units)
                dsVector = self.vector.toDSVector(units)
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
        def toDSLine(self, units):
                dsStartPt = self.start.toDSPoint(units)
                dsEndPt = self.end.toDSPoint(units)
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
        def toDSCircle(self, units):
                dsPlane = self.plane.toDSPlane(units)
                dsCircle = ds.Geometry.Circle.ByPlaneRadius(dsPlane, self.radius)
                return dsCircle
        def toRHCircle(self):
                rhPlane = self.plane.toRHPlane()
                rhCircle = rc.Geometry.Circle(rhPlane, self.radius)
                return rhCircle

class MSEllipse(object):

        def __init__(self, plane= None, xRadius= None, yRadius= None):
                self.plane = plane
                self.xRadius = xRadius
                self.yRadius = yRadius
        def addData(self, data):
                self.data = data
        def toDSEllipse(self, units):
                dsPlane = self.plane.toDSPlane(units)
                dsEllipse = ds.Geometry.Ellipse.ByPlaneRadii(dsPlane, self.xRadius, self.yRadius)
                return dsEllipse
        def toRHEllipse(self):
                rhPlane = self.plane.toRHPlane()
                rhEllipse = rc.Geometry.Ellipse(rhPlane, self.xRadius, self.yRadius)
                return rhEllipse

class MSArc(object):

        def __init__(self, startPoint= None, centerPoint= None, endPoint= None):
                self.centerPoint = centerPoint
                self.startPoint = startPoint
                self.endPoint = endPoint
        def addData(self, data):
                self.data = data
        def toDSArc(self, units):
                dsStartPt = self.startPoint.toDSPoint(units)
                dsEndPt = self.endPoint.toDSPoint(units)
                dsCenterPt = self.centerPoint.toDSPoint(units)
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
        def toDSPolyCurve(self, units):
                dsLines = []
                for line in self.segments:
                        dsLines.append(line.toDSLine(units))
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
        def toDSNurbsCurve(self, units):
                dsPoints = []
                dsWeights = []
                for index, pt in enumerate(self.points):
                        dsPoints.append(pt.toDSPoint(units))
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
        def toDSPolyCurve(self, units):
                dsSubCurves = []
                for crv in self.curves:
                        if type(crv) == MSLine:
                                dsSubCurves.append(crv.toDSLine(units))
                        elif type(crv) == MSArc:
                                dsSubCurves.append(crv.toDSArc(units))
                        elif type(crv) == MSPolyLine:
                                dsSubCurves.append(crv.toDSPolyCurve(units))
                        elif type(crv) == MSNurbsCurve:
                                dsSubCurves.append(crv.toDSNurbsCurve(units).ToNurbsCurve())
                dsPolyCurve = ds.Geometry.PolyCurve.ByJoinedCurves(dsSubCurves)
                return dsPolyCurve
        def toRHPolyCurve(self):
                rhSubCurves = []
                for crv in self.curves:
                        if type(crv) == MSLine:
                                rhSubCurves.append(crv.toRHLineCurve())
                        elif type(crv) == MSArc:
                                rhSubCurves.append(rc.Geometry.ArcCurve(crv.toRHArc()))
                        elif type(crv) == MSNurbsCurve:
                                rhSubCurves.append(crv.toRHNurbsCurve())
                return rc.Geometry.Curve.JoinCurves(rhSubCurves)

class MSMeshFace(object):
        def __init__(self, a= None, b= None, c= None, d= None):
                self.a = a
                self.b = b
                self.c = c
                self.d = d
                self.count = 3 if self.d is None else 4
        def addData(self, data):
                self.data = data
        def toDSMeshFace(self):
                if self.count == 3:
                        dsMeshFace = ds.Geometry.IndexGroup.ByIndices(self.a, self.b, self.c)
                else:
                        dsMeshFace = ds.Geometry.IndexGroup.ByIndices(self.a, self.b, self.c, self.d)
                return dsMeshFace
        def toRHMeshFace(self):
                if self.count == 3:
                        rhMeshFace = rc.Geometry.MeshFace(self.a, self.b, self.c)
                else:
                        rhMeshFace = rc.Geometry.MeshFace(self.a, self.b, self.c, self.d)
                return rhMeshFace

class MSMesh(object):

        def __init__( self, points= None, faces= None):
                self.points = points
                self.faces = faces
        def addData(self, data):
                self.data = data
        def toDSMesh(self, units):
                dsIndexGroups = []
                for i in self.faces:
                        if i.count == 3:
                                dsIndexGroups.append(ds.Geometry.IndexGroup.ByIndices(i.a, i.b, i.c))
                        else:
                                dsIndexGroups.append(ds.Geometry.IndexGroup.ByIndices(i.a, i.b, i.c, i.d))
                dsVertexPositions = []
                for i in self.points:
                        dsVertexPositions.append(i.toDSPoint(units))
                dsMesh = ds.Geometry.Mesh.ByPointsFaceIndices(dsVertexPositions, dsIndexGroups)
                return dsMesh
        def toRHMesh(self):
                rhMesh = rc.Geometry.Mesh()
                for pt in self.points:
                        rhMesh.Vertices.Add(pt.toRHPoint3d())
                rhFaces = []
                for face in self.faces:
                        rhFaces.append(face.toRHMeshFace())
                rhFaceArray = Array[rc.Geometry.MeshFace](rhFaces)
                rhMesh.Faces.AddFaces(rhFaceArray)
                return rhMesh

class MSNurbsSurface(object):

        def __init__(self, points= None, weights= None, knotsU= None, knotsV= None, degreeU= None, degreeV= None, countU= None, countV= None, rational= None):
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
        def toDSNurbsSurface(self, units):
                # DS Requires Control Points to be in .Net typed arrays
                # convert Rhino Control Points to ArrayArray
                # get control points and weights 
                dsControlPoints, dsWeights = [], []
                for pt in self.points:
                        dsControlPoints.append(pt.toDSPoint(units))
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
                for index, _list in enumerate(self.points):
                        for pt in _list:
                                controlPts[index].append(pt.toRHPoint3d())
                for i, _list in enumerate(controlPts):
                        for j, _item in enumerate(_list):
                              rhNurbsSurface.Points.SetControlPoint(i,j, rc.Geometry.ControlPoint(_item))
                return rhNurbsSurface
