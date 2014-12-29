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

def toMSLine(item):
	msStartPt = MSPoint(item.StartPoint.X, item.StartPoint.Y, item.StartPoint.Z)
	msEndPt = MSPoint(item.EndPoint.X, item.EndPoint.Y, item.EndPoint.Z)
	return MSLine(msStartPt, msEndPt)

def toMSPoint(item):
	return MSPoint(item.X, item.Y, item.Z)

def toMSArc(item):
	msStartPt = toMSPoint(item.StartPoint)
	msEndPt = toMSPoint(item.EndPoint)
	msMidPoint = toMSPoint(item.PointAtParameter(0.5))
	return MSArc(msStartPt, msMidPoint, msEndPt)

def toMSEllipse(item):
	msOrigin = toMSPoint(item.CenterPoint)
	msVector = MSVector(item.Normal.X, item.Normal.Y, item.Normal.Z)
	msPlane = MSPlane(msOrigin, msVector)
	return MSEllipse(msPlane, item.MinorAxis.Length, item.MajorAxis.Length)

def toMSCircle(item):
	msOrigin = toMSPoint(item.CenterPoint)
	msVector = MSVector(item.Normal.X, item.Normal.Y, item.Normal.Z)
	msPlane = MSPlane(msOrigin, msVector)
	return MSCircle(msPlane, item.Radius)

def toMSNurbsCurve(item):
	msPoints4d = []
	for pt, w in zip(item.ControlPoints(), item.Weights()):
		msPoints4d.append(MSPoint4d(pt.X, pt.Y, pt.Z, w))
	return MSNurbsCurve(msPoints4d, item.Weights(), item.Knots(), item.Degree)

# use these two functions to convert generic Curve
# to Line or Arc since PolyCurve.Curves() method
# returns only generic curves
def tryGetLine(item):
	startPoint = item.StartPoint
	endPoint = item.EndPoint
	distance = startPoint.DistanceTo(endPoint)
	if round(item.Length, 4) == round(distance, 4):
		return Line.ByStartPointEndPoint(startPoint, endPoint)
	else:
		return None
def tryGetArc(item):
	startPoint = item.StartPoint
	endPoint = item.EndPoint
	tangent = item.TangentAtParameter(0)
	dsArc = Arc.ByStartPointEndPointStartTangent(startPoint, endPoint, tangent)
	if round(dsArc.Length, 4) == round(item.Length, 4):
		return dsArc
	else:
		return None
"""
# this is still work in progress
def toMSPolyLine(item):
	segments, msSegments = [], []
	for crv in item.Curves():
		segments.append(tryGetLine(crv))
	if all(type(x) == Line for x in segments):
		for i in segments:
			msSegments.append(toMSLine(i))
		return MSPolyLine(msSegments)
	else:
		return None

def toMSPolyCurve(item):
	segments = []
	for crv in item.Curves():
		if tryGetLine(crv) != None:
			segments.append(toMSLine(tryGetLine(crv)))
		elif tryGetArc(crv) != None:
			segments.append(toMSArc(tryGetArc(crv)))
		else:
			segments.append(toMSNurbsCurve(crv.ToNurbsCurve()))
	return segments
"""
def toMSMesh(item):
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

def toMSNurbsSurface(item):
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

# funtions to convert DS Geometry to MS Geometry
# Points
def toMSObject(item):
	if type(item) == Point:
		return MSPoint(item.X, item.Y, item.Z)
	elif type(item) == Line:
		return toMSLine(item)
#	elif type(item) == PolyCurve:
#		return toMSPolyCurve(item)
	elif type(item) == Circle:
		return toMSCircle(item)
	elif type(item) == Ellipse:
		return toMSEllipse(item)
	elif type(item) == Arc:
		return toMSArc(item)
	elif type(item) == NurbsCurve:
		return toMSNurbsCurve(item)
	elif type(item) == Mesh:
		return toMSMesh(item)
	elif type(item) == NurbsSurface:
		return toMSNurbsSurface(item)
	else:
		return MSData(item)

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
