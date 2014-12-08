#Copyright(c) 2014, Konrad K Sobon
#@arch_laboratory, http://archi-lab.net

"""
This component exports serialized geometry to specified location. Thank you to Mostapha Sadeghipour Roudsari
for providing invaluable help with this project. 

    Args:
        _geometry: any GH/or rhino referenced geometry
        _filePath: A local folder with file name and extension ex. C:\test.geo
        _export: Set Boolean to True to export geometry to destination folder
"""

ghenv.Component.Name = "Mantis Shrimp - Export"
ghenv.Component.NickName = 'exportMantisShrimp'
ghenv.Component.Category = "Mantis Shrimp"

import sys
# change this to where you library is
sys.path.append(r"C:\Users\ksobon\AppData\Roaming\Dynamo\0.7\packages\Mantis Shrimp\extra")
from mantisshrimp import *

import Rhino as rc
import cPickle as pickle
import os
import Grasshopper.Kernel as gh

class SerializeObjects(object):
    
    def __init__(self, filePath, data = None):
        
        # create directory if it is not created
        folder, fileName = os.path.split(filePath)
        if not os.path.isdir(folder):
            os.mkdir(folder)
        
        self.filePath = filePath
        self.data = data
   
    def convertPolyCurveToCurve(self):
        placeHolder = range(len(self.data))
        
        for geoCount, geo in enumerate(self.data):
            if type(geo) == rc.Geometry.PolyCurve:
                placeHolder[geoCount] = geo.ToNurbsCurve()
            else:
                placeHolder[geoCount] = geo
        
        self.data = placeHolder
        
    def saveToFile(self):
        try:
            with open(self.filePath, 'wb') as outf:
                pickle.dump(self.data, outf)
        except:
            # check input data and convert PolyCurves to NurbsCurve
            # In some cases pickle crashes while exporting polycurves
            self.convertPolyCurveToCurve()
            with open(self.filePath, 'wb') as outf:
                pickle.dump(self.data, outf)
            
    def readFromFile(self):
        with open(self.filePath, 'rb') as inf:
            self.data = pickle.load(inf)


geometryOut = []
if _export:
    for item in geometry:
        if type(item) == rc.Geometry.Point3d:
            msPoint = MSPoint(item.X, item.Y, item.Z)
            geometryOut.append(msPoint)
        elif type(item) == rc.Geometry.LineCurve:
            msStartPt = MSPoint(item.PointAtStart.X, item.PointAtStart.Y, item.PointAtStart.Z)
            msEndPt = MSPoint(item.PointAtEnd.X, item.PointAtEnd.Y, item.PointAtEnd.Z)
            geometryOut.append(MSLine(msStartPt, msEndPt))
        elif type(item) == rc.Geometry.PolyCurve and item.IsPolyline() == True:
            segments = []
            for i in range(0, item.SegmentCount,1):
                line = item.SegmentCurve(i)
                msStartPt = MSPoint(line.PointAtStart.X, line.PointAtStart.Y, line.PointAtStart.Z)
                msEndPt = MSPoint(line.PointAtEnd.X, line.PointAtEnd.Y, line.PointAtEnd.Z)
                segments.append(MSLine(msStartPt, msEndPt))
            geometryOut.append(MSPolyLine(segments))
        elif type(item) == rc.Geometry.NurbsCurve and item.IsEllipse() == True:
            item = item.TryGetEllipse()[1]
            msVector = MSVector(item.Plane.Normal.X,item.Plane.Normal.Y, item.Plane.Normal.Z) 
            msOrigin = MSPoint(item.Plane.Origin.X, item.Plane.Origin.Y, item.Plane.Origin.Z)
            msPlane = MSPlane(msOrigin, msVector)
            geometryOut.append(MSEllipse(msPlane, item.Radius1, item.Radius2))
        elif type(item) == rc.Geometry.ArcCurve and item.IsCircle() == True:
            item = item.TryGetCircle()[1]
            msVector = MSVector(item.Normal.X,item.Normal.Y, item.Normal.Z)
            msOrigin = MSPoint(item.Center.X, item.Center.Y, item.Center.Z)
            msPlane = MSPlane(msOrigin, msVector)
            geometryOut.append(MSCircle(msPlane, item.Radius))
        elif type(item) == rc.Geometry.ArcCurve and item.IsArc() == True:
            item = item.TryGetArc()[1]
            startPoint = MSPoint(item.StartPoint.X, item.StartPoint.Y, item.StartPoint.Z)
            midPoint = MSPoint(item.MidPoint.X, item.MidPoint.Y, item.MidPoint.Z)
            endPoint = MSPoint(item.EndPoint.X, item.EndPoint.Y, item.EndPoint.Z)
            geometryOut.append(MSArc(startPoint, midPoint, endPoint))
        elif type(item) == rc.Geometry.NurbsCurve and item.SpanCount == 1:
            msControlPoints = []
            for pt in item.Points:
                msControlPoints.append(MSPoint4d(pt.Location.X, pt.Location.Y, pt.Location.Z, pt.Weight))
            knots = []
            for i in range(0, item.Knots.Count, 1):
                knots.append(item.Knots[i])
            # weights information is stored in control points
            weights = None
            spanCount = item.SpanCount
            geometryOut.append(MSNurbsCurve(msControlPoints, weights, knots, item.Degree, spanCount))
#        elif type(item) == rc.Geometry.NurbsCurve and item.SpanCount > 1:
#            
#        elif type(item) == rc.Geometry.PolyCurve:
#            
        elif type(item) == rc.Geometry.Mesh:
            msFaces = []
            for i in range(0, item.Faces.Count, 1):
                face = item.Faces.Item[i]
                if face.IsQuad:
                    msFaces.append(MSMeshFace(face.A, face.B, face.C, face.D))
                else:
                    msFaces.append(MSMeshFace(face.A, face.B, face.C))
            msPoints = []
            for i in range(0, item.Vertices.Count, 1):
                msPoints.append(MSPoint(item.Vertices.Item[i].X, item.Vertices.Item[i].Y, item.Vertices.Item[i].Z))
            geometryOut.append(MSMesh(msPoints, msFaces))
        elif type(item) == rc.Geometry.Brep and item.IsSurface == True:
            item = item.Faces[0].ToNurbsSurface()
            msControlPoints = []
            for pt in item.Points:
                msControlPoints.append(MSPoint4d(pt.Location.X, pt.Location.Y, pt.Location.Z, pt.Weight))
            # since weights in Rhino are stored in points 
            # they will be extracted from MSPoint4d
            weights = None
            knotsU = []
            for i in range(0, item.KnotsU.Count, 1):
                knotsU.append(item.KnotsU[i])
            knotsV = []
            for i in range(0, item.KnotsV.Count, 1):
                knotsV.append(item.KnotsV[i])
            geometryOut.append(MSNurbsSurface(msControlPoints, weights, knotsU, knotsV, item.OrderU, item.OrderV, item.SpanCount(0), item.SpanCount(1), item.IsRational))
        else:
            geometryOut.append(MSData(item))
    try:
        serializer = SerializeObjects(filePath, geometryOut)
        serializer.saveToFile()
        warnType = gh.GH_RuntimeMessageLevel.Remark
        msg = "File is exported to " + filePath + "Now you can use Dynamo to import the file."
    except Exception, e:
        warnType = gh.GH_RuntimeMessageLevel.Warning
        msg = "Failed to export: \n" + `e`
else:
    msg = "Export set to false."

ghenv.Component.AddRuntimeMessage(warnType, msg)

print(geometryOut)
