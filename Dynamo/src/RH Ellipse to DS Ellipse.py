#Copyright(c) 2015, Konrad Sobon
# @arch_laboratory, http://archi-lab.net

import clr
import sys
clr.AddReference('ProtoGeometry')

pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

import os
appDataPath = os.getenv('APPDATA')
msPath = appDataPath + r'\Dynamo\0.8\packages\Mantis Shrimp\extra'
if msPath not in sys.path:
	sys.path.append(msPath)
rhDllPath = appDataPath + r'\Dynamo\0.8\packages\Mantis Shrimp\bin\Rhino3dmIO.dll'
clr.AddReferenceToFileAndPath(rhDllPath)

from Autodesk.DesignScript.Geometry import *
import Rhino as rc

#The inputs to this node will be stored as a list in the IN variable.
dataEnteringNode = IN
rhObjects = IN[0]

#point/control point conversion function
def rhPointToPoint(rhPoint):
	rhPointX = rhPoint.Location.X
	rhPointY = rhPoint.Location.Y
	rhPointZ = rhPoint.Location.Z
	return Point.ByCoordinates(rhPointX, rhPointY, rhPointZ)

def rhEllipseToEllipse(item):
	pt0 = rhPointToPoint(item.Points[0])
	pt2 = rhPointToPoint(item.Points[2])
	pt4 = rhPointToPoint(item.Points[4])
	origin = Line.ByStartPointEndPoint(pt0, pt4).PointAtParameter(0.5)
	vector1 = Vector.ByTwoPoints(origin, pt2)
	vector2 = Vector.ByTwoPoints(origin, pt4)
	ellipse = Ellipse.ByOriginVectors(origin, vector1, vector2)
	pt0.Dispose()
	pt2.Dispose()
	pt4.Dispose()
	origin.Dispose()
	vector1.Dispose()
	vector2.Dispose()
	return ellipse

#convert rhino/gh geometry to ds geometry
try:
	errorReport = None
	dsEllipse = []
	for i in rhObjects:
		try:
			i = i.Geometry
		except:
			pass
		if i.ToString() == "Rhino.Geometry.NurbsCurve":
			if i.IsClosed and i.IsRational:
				dsEllipse.append(rhEllipseToEllipse(i))
except:
	# if error accurs anywhere in the process catch it
	import traceback
	errorReport = traceback.format_exc()

#Assign your output to the OUT variable
if errorReport == None:
	OUT = dsEllipse
else:
	OUT = errorReport
