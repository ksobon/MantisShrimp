#Copyright(c) 2014, Konrad Sobon
# @arch_laboratory, http://archi-lab.net

import clr
import sys
RhinoIOPath = r'C:\Program Files\Dynamo 0.7'
if RhinoIOPath not in sys.path:
	sys.path.Add(RhinoIOPath)
clr.AddReference('ProtoGeometry')
clr.AddReferenceToFileAndPath(RhinoIOPath + r"\Rhino3dmIO.dll")

comtypes_path = r'C:\Program Files (x86)\IronPython 2.7\Lib\comtypes-1.0.0'
psutil_path = r'C:\Program Files (x86)\IronPython 2.7\Lib\psutil-2.1.1'
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(comtypes_path)
sys.path.append(psutil_path)
sys.path.append(pyt_path)

import Rhino as rc
import comtypes.client as cc
import comtypes
import os
import System

rhFilePath = str(IN[0])
ghFilePath = str(IN[1])

#pids = []
#a = os.popen("tasklist").readlines()
#for x in a:
#	if "Rhino.exe" in x:
#		try:
#			pids.append(x[29:34])
#		except:
#			pass

rhinoId = "Rhino5x64.Application"
type = System.Type.GetTypeFromProgID(rhinoId)
rhinoApp = System.Activator.CreateInstance(type)
rhinoApp.Visible = True

path = "_Open "
path += rhFilePath
rhinoApp.RunScript("-_Open D:\11_Grimshaw Architects\Playgrounds\RHINO\01-light.3dm")


#rhinoApp.RunScript("_Grasshopper", 0)
#gh = rhinoApp.GetPlugInObject("b45a29b1-4343-4035-989e-044e8580d9cf", "00000000-0000-0000-0000-000000000000")
#gh.OpenDocument(ghFilePath)


OUT = strFile

