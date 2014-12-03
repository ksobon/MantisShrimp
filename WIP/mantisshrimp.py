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


#data class
class MSData(object):

        def __init__(self, _data = None):
                self.data = _data

        def addData(self, data):
                self.data = data

#geometry classes
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
