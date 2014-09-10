#Copyright(c) 2014, Konrad Sobon
# @arch_laboratory, http://archi-lab.net

import clr
import sys
RhinoIOPath = r'C:\Program Files\Dynamo 0.7'
if RhinoIOPath not in sys.path:
	sys.path.Add(RhinoIOPath)
clr.AddReference('ProtoGeometry')
clr.AddReferenceToFileAndPath(RhinoIOPath + r"\Rhino3dmIO.dll")
from Autodesk.DesignScript.Geometry import *
import Rhino as rc

#The inputs to this node will be stored as a list in the IN variable.
dataEnteringNode = IN
rhModel = IN[0]
rhLayer = IN[1]

#get objects by layer
#Assign your output to the OUT variable
OUT = rhModel.Objects.FindByLayer(rhLayer)
