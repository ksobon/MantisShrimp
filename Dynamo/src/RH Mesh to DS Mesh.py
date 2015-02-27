#Copyright(c) 2015, Konrad Sobon
# @arch_laboratory, http://archi-lab.net

import clr
import sys
clr.AddReference('ProtoGeometry')

pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

import os
appDataPath = os.getenv('APPDATA')
msPath = appDataPath + r"\Dynamo\0.7\packages\Mantis Shrimp\extra"
rhPath = appDataPath + r"\Dynamo\0.7\packages\Mantis Shrimp\bin"
rhDllPath = appDataPath + r"\Dynamo\0.7\packages\Mantis Shrimp\bin\RhinoCommon.dll"
if msPath not in sys.path:
	sys.path.Add(msPath)
if rhPath not in sys.path:
	sys.path.Add(rhPath)
	clr.AddReferenceToFileAndPath(rhDllPath)

from Autodesk.DesignScript.Geometry import *
import Rhino as rc

#The inputs to this node will be stored as a list in the IN variable.
dataEnteringNode = IN
rhObjects = IN[0]
_units = IN[1]

#unit conversion function from Rhino to DS
def toDSUnits(_units):
	if _units == rc.UnitSystem.Millimeters:
		return 0.001
	elif _units == rc.UnitSystem.Centimeters:
		return 0.01
	elif _units == rc.UnitSystem.Decimeters:
		return 0.1
	elif _units == rc.UnitSystem.Meters:
		return 1
	elif _units == rc.UnitSystem.Inches:
		return 0.0254
	elif _units == rc.UnitSystem.Feet:
		return 0.3048
	elif _units == rc.UnitSystem.Yards:
		return 0.9144

#3dPoint Conversion function
def rhPoint3dToPoint(rhPoint):
	rhPointX = rhPoint.X * toDSUnits(_units)
	rhPointY = rhPoint.Y * toDSUnits(_units)
	rhPointZ = rhPoint.Z * toDSUnits(_units)
	dsPoint = Point.ByCoordinates(rhPointX, rhPointY, rhPointZ)
	return dsPoint

def rhMeshToMesh(rhMesh):
	vertexPositions, indices, indexGroups = [], [], []
	faces = rhMesh.Faces
	topologyVerticesList = rhMesh.TopologyVertices
	for i in range(0, rhMesh.Faces.Count, 1):
		indices.append(faces.GetTopologicalVertices(i))
	for i in range(0, topologyVerticesList.Count, 1):
		vertexPositions.append(rhPoint3dToPoint(topologyVerticesList.Item[i]))
	for i in indices:
		if len(i) == 3:
			a = i[0]
			b = i[1]
			c = i[2]
			indexGroups.append(IndexGroup.ByIndices(a,b,c))
		elif len(i) == 4:
			a = i[0]
			b = i[1]
			c = i[2]
			d = i[3]
			indexGroups.append(IndexGroup.ByIndices(a,b,c,d))
	dsMesh = Mesh.ByPointsFaceIndices(vertexPositions, indexGroups)
	del vertexPositions[:]
	del indices[:]
	del indexGroups[:]
	return dsMesh

#convert rhino/gh geometry to ds geometry
dsMeshes = []
for i in rhObjects:
	try:
		i = i.Geometry
	except:
		pass
	if i.ToString() == "Rhino.Geometry.Mesh":
		dsMeshes.append(rhMeshToMesh(i))

#Assign your output to the OUT variable
OUT = dsMeshes
