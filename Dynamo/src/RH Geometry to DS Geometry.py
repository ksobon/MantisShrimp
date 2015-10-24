# Copyright(c) 2015, Konrad Sobon
# @arch_laboratory, http://archi-lab.net

import clr
import sys

pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

import os
appDataPath = os.getenv('APPDATA')
msPath = appDataPath + r'\Dynamo\0.8\packages\Mantis Shrimp\extra'
if msPath not in sys.path:
	sys.path.append(msPath)
rhDllPath = appDataPath + r'\Dynamo\0.8\packages\Mantis Shrimp\bin\Rhino3dmIO.dll'
clr.AddReferenceToFileAndPath(rhDllPath)

import Rhino as rc
from mantisshrimp import rhLineToLine, rhPointToPoint, rhBrepToPolySurface, rhCurveToPolyCurve, rhMeshToMesh, rhNurbsSurfaceToSurface, rhArcToArc, rhSingleSpanNurbsCurveToCurve, rhEllipseToEllipse, rhCircleToCircle, rhPolyCurveToPolyCurve

#The inputs to this node will be stored as a list in the IN variable.
dataEnteringNode = IN

if isinstance(IN[0], list):
	rhObjects = IN[0]
else:
	rhObjects = [IN[0]]

def GetGeometry(rhObj):
	try:
		geo = rhObj.Geometry
		if geo.ToString() == "Rhino.Geometry.LineCurve":
			return rhLineToLine(geo)
		elif geo.ToString() == "Rhino.Geometry.ArcCurve" and geo.IsArc():
			return rhArcToArc(geo)
		elif geo.ToString() == "Rhino.Geometry.Point":
			return rhPointToPoint(geo)
		elif geo.ToString() == "Rhino.Geometry.NurbsCurve" and geo.IsClosed and geo.IsRational:
			return rhEllipseToEllipse(geo)
		elif geo.ToString() == "Rhino.Geometry.PolyCurve":
			return rhPolyCurveToPolyCurve(geo)
		elif geo.ToString() == "Rhino.Geometry.NurbsCurve":
			return rhSingleSpanNurbsCurveToCurve(geo)
		elif geo.ToString() == "Rhino.Geometry.Extrusion":
			brep = geo.ToBrep()
			return rhBrepToPolySurface(brep)
		elif geo.ToString() == "Rhino.Geometry.PolylineCurve":
			return rhCurveToPolyCurve(geo)
		elif geo.ToString() == "Rhino.Geometry.Mesh":
			return rhMeshToMesh(geo)
	except:
		try:
			geo = rhObj.Geometry
			if geo.ToString() == "Rhino.Geometry.Brep":
				brepFaces = geo.Faces
				faceList = []
				for i in range(0, brepFaces.Count, 1):
					rhSurface = brepFaces.Item[i].UnderlyingSurface()
					if rhSurface.ToString() == "Rhino.Geometry.NurbsSurface":
						faceList.append(rhNurbsSurfaceToSurface(rhSurface))
					elif rhSurface.ToString() == "Rhino.Geometry.RevSurface":
						faceList.append(rhNurbsSurfaceToSurface(rhSurface.ToNurbsSurface()))
				return faceList
			elif geo.ToString() == "Rhino.Geometry.ArcCurve" and geo.IsCircle():
				return rhCircleToCircle(geo)
		except:
			try:
				geo = rhObj.Geometry
				if geo.ToString() == "Rhino.Geometry.Brep":
					return rhBrepToPolySurface(geo)
			except:
				pass

def ProcessList(_func, _list):
	return map(lambda x: ProcessList(_func, x) if type(x) == list else _func(x) , _list)

#convert rhino/gh geometry to ds geometry
try:
	errorReport = None
	dsGeometry = ProcessList(GetGeometry, rhObjects)
except:
	# if error accurs anywhere in the process catch it
	import traceback
	errorReport = traceback.format_exc()
	
#Assign your output to the OUT variable
if errorReport == None:
	OUT = dsGeometry
else:
	OUT = errorReport
