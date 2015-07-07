#Copyright(c) 2015, Konrad Sobon
# @arch_laboratory, http://archi-lab.net

import clr
import sys
clr.AddReference('ProtoGeometry')

pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

import os
appDataPath = os.getenv('APPDATA')
msPath = appDataPath + r"\Dynamo\0.8\packages\Mantis Shrimp\extra"
if msPath not in sys.path:
	sys.path.append(msPath)
txtFilePath = appDataPath + r"\Dynamo\0.8\packages\Mantis Shrimp\extra\rhPath.txt"
if not os.path.isfile(txtFilePath):
	message = "Provide valid RhinoCommon.dll path."
else:
	file = open(txtFilePath, 'r+')
	rhDllPath = file.readline()
	clr.AddReferenceToFileAndPath(rhDllPath)
	file.close()

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

def process_list(_func, _list):
    return map( lambda x: process_list(_func, x) if type(x)==list else _func(x), _list )

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

def tryGetArc(item):
	startPoint = item.StartPoint
	endPoint = item.EndPoint
	tangent = item.TangentAtParameter(0)
	dsArc = Arc.ByStartPointEndPointStartTangent(startPoint, endPoint, tangent)
	if round(dsArc.Length, 4) == round(item.Length, 4):
		return dsArc
	else:
		return None

def tryGetLine(item):
	startPoint = item.StartPoint
	endPoint = item.EndPoint
	distance = startPoint.DistanceTo(endPoint)
	if round(item.Length, 4) == round(distance, 4):
		return Line.ByStartPointEndPoint(startPoint, endPoint)
	else:
		return None

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

def toMSMesh(item):
	msPoints = []
	for pt in item.VertexPositions:
		msPoints.append(MSPoint(pt.X, pt.Y, pt.Z))
	faceTopology = []
	for i in item.FaceIndices:
		if i.Count == 3:
			faceTopology.append([i.A, i.B, i.C])
		else:
			faceTopology.append([i.A, i.B, i.C, i.D])
	return MSMesh(msPoints, faceTopology)

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

def toMSObject(item):
	if type(item) == Point:
		return MSPoint(item.X, item.Y, item.Z)
	elif type(item) == Line:
		return toMSLine(item)
	elif type(item) == PolyCurve:
		if toMSPolyLine(item) == None:
			print("None")
		else:
			return toMSPolyLine(item)
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
