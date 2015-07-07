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

#3dPoint Conversion function
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
	# According to Dynamo dev team it's required to dispose of unused geometry.
	for i in vertexPositions:
		i.Dispose()
	return dsMesh

try:
	errorReport = None
	#convert rhino/gh geometry to ds geometry
	dsMeshes = []
	for i in rhObjects:
		try:
			i = i.Geometry
		except:
			pass
		if i.ToString() == "Rhino.Geometry.Mesh":
			dsMeshes.append(rhMeshToMesh(i))
except:
	# if error accurs anywhere in the process catch it
	import traceback
	errorReport = traceback.format_exc()

#Assign your output to the OUT variable
if errorReport == None:
	OUT = dsMeshes
else:
	OUT = errorReport
