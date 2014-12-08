"""
Copyright(c) 2014, Konrad Sobon
@arch_laboratory, http://archi-lab.net

Grasshopper and Dynamo interop library

"""
import clr
import sys
sys.path.append(r"C:\Program Files\Dynamo 0.7")
clr.AddReference('ProtoGeometry')

RhinoCommonPath = r'C:\Program Files\Rhinoceros 5 (64-bit)\System'
if RhinoCommonPath not in sys.path:
	sys.path.Add(RhinoCommonPath)
clr.AddReferenceToFileAndPath(RhinoCommonPath + r"\RhinoCommon.dll")

pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

from System import Array
from System.Collections.Generic import *
import Autodesk.DesignScript as ds
import Rhino as rc
import pickle

""" Misc Functions """
def process_list(_func, _list):
    return map( lambda x: process_list(_func, x) if type(x)==list else _func(x), _list )

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

        def __init__(self, plane= None, xRadius= None, yRadius= None):
                self.plane = plane
                self.xRadius = xRadius
                self.yRadius = yRadius
        def addData(self, data):
                self.data = data
        def toDSEllipse(self):
                dsPlane = self.plane.toDSPlane()
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
        def toDSArc(self):
                dsStartPt = self.startPoint.toDSPoint()
                dsEndPt = self.endPoint.toDSPoint()
                dsCenterPt = self.centerPoint.toDSPoint()
                return ds.Geometry.Arc.ByCenterPointStartPointEndPoint(dsCenterPt, dsStartPt, dsEndPt)
        def toRHArc(self):
                rhStartPt = self.startPoint.toRHPoint3d()
                rhEndPt = self.endPoint.toRHPoint3d()
                rhCenterPt = self.centerPoint.toRHPoint3d()
                return rc.Geometry.Arc(rhStartPt, rhCenterPt, rhEndPt)

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

        def __init__( self, points= None, weights= None, knots= None, degree= None, spanCount= None):
                self.points = points
                self.weights = weights
                self.knots = knots
                self.degree = degree
                self.spanCount = spanCount
        def addData(self, data):
                self.data = data
        def toDSSingleSpanNurbsCurve(self):
                dsPoints, dsWeights = [], []
                for pt in self.points:
                        dsPoints.append(pt.toDSPoint())
                        dsWeights.append(pt.weight)
                dsPtArray = Array[ds.Geometry.Point](dsPoints)
                dsWeightsArray = Array[float](dsWeights)
                dsKnots = []
                for i in self.knots:
                        dsKnots.append(i)
                dsKnots.insert(0, dsKnots[0])
                dsKnots.insert(len(dsKnots), dsKnots[(len(dsKnots)-1)])
                dsNurbsCurve = ds.Geometry.NurbsCurve.ByControlPointsWeightsKnots(dsPtArray, dsWeightsArray, dsKnots, self.degree)
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
""" working
class MSPolyCurve(object):

        def __init__(self, curves= None):
                self.curves = curves
        def addData(self, data):
                self.data = data
        def toDSPolyCurve(self):
                dsPolyCurve = []
                for crv in self.curves:
                        if type(crv) == MSLine:
                                dsPolyCurve.append(crv.toDSLine())
                        elif type(crv) == MSArc:
                                dsPolyCurve.append(crv.toDSArc())
                        elif type(crv) == MSPolyLine:
                                dsPolyCurve.append(crv.toDSPolyCurve())
#                        elif type(crv) == 
                                
 working """
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
        def toDSMesh(self):
                dsIndexGroups = []
                for i in self.faces:
                        if i.count == 3:
                                dsIndexGroups.append(ds.Geometry.IndexGroup.ByIndices(i.a, i.b, i.c))
                        else:
                                dsIndexGroups.append(ds.Geometry.IndexGroup.ByIndices(i.a, i.b, i.c, i.d))
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
                for index, _list in enumerate(self.points):
                        for pt in _list:
                                controlPts[index].append(pt.toRHPoint3d())
                for i, _list in enumerate(controlPts):
                        for j, _item in enumerate(_list):
                              rhNurbsSurface.Points.SetControlPoint(i,j, rc.Geometry.ControlPoint(_item))
                return rhNurbsSurface
