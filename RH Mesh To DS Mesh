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

import Rhino as rc
from Autodesk.DesignScript.Geometry import *
import math

#The inputs to this node will be stored as a list in the IN variable.
dataEnteringNode = IN
rhObjects = IN[0]

#3dPoint Conversion
def rhPoint3dToPoint(rhPoint):
	rhPointX = rhPoint.X
	rhPointY = rhPoint.Y
	rhPointZ = rhPoint.Z
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
