#Copyright(c) 2014, Konrad Sobon
# @arch_laboratory, http://archi-lab.net

import clr
import sys
clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *

# Import DocumentManager and TransactionManager
clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

# Import RevitAPI
clr.AddReference("RevitAPI")
import Autodesk
from Autodesk.Revit.DB import *

doc = DocumentManager.Instance.CurrentDBDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application

pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

from Autodesk.DesignScript.Geometry import *

from System import Array
from System.Collections.Generic import *
import math

#The inputs to this node will be stored as a list in the IN variable.
dataEnteringNode = IN
dsObjects = IN[0]
_lineStyle = UnwrapElement(IN[1][0])

def toRvtPoint(point):
	unitsFactor = 3.28084 #Revit works in Feet while Dynamo in Meters
	x = point.X * unitsFactor
	y = point.Y * unitsFactor
	z = point.Z * unitsFactor
	return XYZ(x,y,z)
	
def toRvtType(dsObject):
	if type(dsObject) == NurbsCurve:
		points = []
		subCurves = dsObject.DivideEqually(16)
		for i in subCurves:
			points.append(i.StartPoint)
		points.insert(len(points), subCurves[(len(subCurves)-1)].EndPoint)
		controlPoints = List[XYZ]()
		for i in points:
			controlPoints.Add(toRvtPoint(i))
		tangents = Autodesk.Revit.DB.HermiteSplineTangents()
		endTangent = toRvtPoint(dsObject.TangentAtParameter(1))
		startTangent = toRvtPoint(dsObject.TangentAtParameter(0))
		tangents.EndTangent = endTangent.Normalize()
		tangents.StartTangent = startTangent.Normalize()
		return Autodesk.Revit.DB.HermiteSpline.Create(controlPoints, False, tangents)	
	elif type(dsObject) == Arc:
		#convert DS Arc to Revit Arc
		startPt = toRvtPoint(dsObject.StartPoint)
		endPt = toRvtPoint(dsObject.EndPoint)
		midPt = toRvtPoint(dsObject.PointAtParameter(0.5))
		return Autodesk.Revit.DB.Arc.Create(startPt, endPt, midPt)
	elif type(dsObject) == Line:
		#convert DS Line to Revit Line
		startPt = toRvtPoint(dsObject.StartPoint)
		endPt = toRvtPoint(dsObject.EndPoint)
		return Autodesk.Revit.DB.Line.CreateBound(startPt, endPt)
	elif type(dsObject) == Circle:
		#convert DS Circle to Revit Arc (for arcs with 2pi range will be automatically converted to circle)
		center = toRvtPoint(dsObject.CenterPoint)
		radius = dsObject.Radius * 3.28084 #converted to FT from M
		startAngle = 0
		endAngle = 2 * math.pi
		xAxis = XYZ(1,0,0) #has to be normalized
		yAxis = XYZ(0,1,0) #has to be normalized
		return Autodesk.Revit.DB.Arc.Create(center, radius, startAngle, endAngle, xAxis, yAxis)
	else:
		return dsObject.ToRevitType()

def makeRvtDetailLines(crv, _lineStyle):
	detailLine = doc.Create.NewDetailCurve(doc.ActiveView, crv)
	if detailLine != None:
		detailLine.LineStyle = _lineStyle
	return detailLine

def makeRvtDetailLines2(crv, _lineStyle):
	detailLine = doc.Create.NewDetailCurve(doc.ActiveView, crv)
	bipName = BuiltInParameter.BUILDING_CURVE_GSTYLE
	lineStyle = detailLine.get_Parameter(bipName)
	lineStyle.Set(_lineStyle.Id)
	return detailLine

def processListArg(_func, _list, _arg):
	return map( lambda x: processListArg(_func, x, _arg) if type(x)==list else _func(x, _arg), _list )

def process_list(_func, _list):
	return map( lambda x: process_list(_func, x) if type(x)==list else _func(x), _list )

#"Start" the transaction
TransactionManager.Instance.EnsureInTransaction(doc)

rvtElements = process_list(toRvtType, dsObjects)
rvtElements = processListArg(makeRvtDetailLines, rvtElements, _lineStyle)

# "End" the transaction
TransactionManager.Instance.TransactionTaskDone()

#Assign your output to the OUT variable
OUT = rvtElements
