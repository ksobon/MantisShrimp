#Copyright(c) 2014, Konrad Sobon
# @arch_laboratory, http://archi-lab.net

import clr
import sys
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

from Autodesk.DesignScript.Geometry import *
from System import Array
from System.Collections.Generic import *
import Rhino as rc
import pickle
from mantisshrimp import *

#The inputs to this node will be stored as a list in the IN variable.
dataEnteringNode = IN

dsObjects = IN[0]
_filePath = str(IN[1])
_export = IN[2]

class SerializeObjects(object):
    
    def __init__(self, filePath, data = None):
        
        # create directory if it is not created
        folder, fileName = os.path.split(filePath)
        if not os.path.isdir(folder):
            os.mkdir(folder)
        
        self.filePath = filePath
        self.data = data
        
    def saveToFile(self):
        try:
            with open(self.filePath, 'wb') as outf:
                pickle.dump(self.data, outf)
        except:
            with open(self.filePath, 'wb') as outf:
                pickle.dump(self.data, outf)
            
    def readFromFile(self):
        with open(self.filePath, 'rb') as inf:
            self.data = pickle.load(inf)

# recursive function to process any input list and output 
# matching structure list
def process_list(_func, _list):
    return map( lambda x: process_list(_func, x) if type(x)==list else _func(x), _list )
# function to convert DS Point to MS Point
def toMSPoint(_point):
	return MSPoint(_point.X, _point.Y, _point.Z)

# funtions to convert DS Geometry to MS Geometry
# Points
def toMSObject(item):
	if type(item) == Point:
		return MSPoint(item.X, item.Y, item.Z)
	elif type(item) == Line:
		msStartPt = MSPoint(item.StartPoint.X, item.StartPoint.Y, item.StartPoint.Z)
		msEndPt = MSPoint(item.EndPoint.X, item.EndPoint.Y, item.EndPoint.Z)
		return MSLine(msStartPt, msEndPt)
	elif type(item) == PolyCurve:
		segments = []
		for line in item.Curves():
			msStartPt = MSPoint(line.StartPoint.X, line.StartPoint.Y, line.StartPoint.Z)
			msEndPt = MSPoint(line.EndPoint.X, line.EndPoint.Y, line.EndPoint.Z)
			segments.append(MSLine(msStartPt, msEndPt))
		return MSPolyLine(segments)
	elif type(item) == Circle:
		msOrigin = MSPoint(item.CenterPoint.X, item.CenterPoint.Y, item.CenterPoint.Z)
		msVector = MSVector(item.Normal.X, item.Normal.Y, item.Normal.Z)
		msPlane = MSPlane(msOrigin, msVector)
		return MSCircle(msPlane, item.Radius)
	elif type(item) == Ellipse:
		msOrigin = MSPoint(item.CenterPoint.X, item.CenterPoint.Y, item.CenterPoint.Z)
		msVector = MSVector(item.Normal.X, item.Normal.Y, item.Normal.Z)
		msPlane = MSPlane(msOrigin, msVector)
		return MSEllipse(msPlane, item.MinorAxis.Length, item.MajorAxis.Length)
	elif type(item) == Arc:
		msStartPt = MSPoint(item.StartPoint.X, item.StartPoint.Y, item.StartPoint.Z)
		msEndPt = MSPoint(item.EndPoint.X, item.EndPoint.Y, item.EndPoint.Z)
		msCenterPt = MSPoint(item.PointAtParameter(0.5).X, item.PointAtParameter(0.5).Y, item.PointAtParameter(0.5).Z)
		return MSArc(msStartPt, msCenterPt, msEndPt)
	elif type(item) == NurbsCurve:
		msPoints4d = []
		for pt, w in zip(item.ControlPoints(), item.Weights()):
			msPoints4d.append(MSPoint4d(pt.X, pt.Y, pt.Z, w))
		return MSNurbsCurve(msPoints4d, item.Weights(), item.Knots(), item.Degree)
	elif type(item) == Mesh:
		msPoints = []
		for pt in item.VertexPositions:
			msPoints.append(MSPoint(pt.X, pt.Y, pt.Z))
		msFaces = []
		for i in item.FaceIndices:
			if i.Count == 3:
				msFaces.append(MSMeshFace(i.A, i.B, i.C))
			else:
				msFaces.append(MSMeshFace(i.A, i.B, i.C, i.D))
		return MSMesh(msPoints, msFaces)
	elif type(item) == NurbsSurface:
		controlPoints = list(item.ControlPoints())
		msControlPoints = [[] for i in range(len(controlPoints))]
		for index, _list in enumerate(controlPoints):
			for pt in _list:
					msControlPoints[index].append(MSPoint(pt.X, pt.Y, pt.Z))
		rational = item.IsRational
		if rational:
			weights = None
		else:
			weights = item.Weights()
		return MSNurbsSurface(msControlPoints, weights, item.UKnots(), item.VKnots(), item.DegreeU, item.DegreeV, item.NumControlPointsU, item.NumControlPointsV, rational)
	else:
		msData = MSData(item)
		return msData

if _export:
	outGeometry = process_list(toMSObject, dsObjects)
	
	try:
		serializer = SerializeObjects(_filePath, outGeometry)
		serializer.saveToFile()
		message = "File is exported to \n" + _filePath + ".\n" + \
			"Now you can use Grasshopper to import the file."
	except:
		message = "Export failed. Try again."
		pass
else:
	message = "Export set to false."

#Assign your output to the OUT variable
OUT = '\n'.join('{:^35}'.format(s) for s in message.split('\n'))
