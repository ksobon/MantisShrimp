#Copyright(c) 2014, Konrad Sobon
# @arch_laboratory, http://archi-lab.net

import clr
import sys
clr.AddReference('ProtoGeometry')

RhinoCommonPath = r'C:\Program Files\Rhinoceros 5 (64-bit)\System'
if RhinoCommonPath not in sys.path:
	sys.path.Add(RhinoCommonPath)
clr.AddReferenceToFileAndPath(RhinoCommonPath + r"\RhinoCommon.dll")

pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

ms_path = r'C:\Users\ksobon\AppData\Roaming\Dynamo\0.7\packages\Mantis Shrimp\extra'
if ms_path not in sys.path:
	sys.path.Add(ms_path)

from Autodesk.DesignScript.Geometry import *
from System import Array
from System.Collections.Generic import *
import Rhino as rc
import pickle
from mantisshrimp import *
import os

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

# recursive function to process any input list and output 
# matching structure list
def process_list(_func, _list):
    return map( lambda x: process_list(_func, x) if type(x)==list else _func(x), _list )

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
