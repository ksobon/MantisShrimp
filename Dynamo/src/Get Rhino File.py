# Copyright(c) 2015, Konrad Sobon
# @arch_laboratory, http://archi-lab.net

import clr
import sys

pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

import os
appDataPath = os.getenv('APPDATA')
msPath = appDataPath + r'\Dynamo\0.9\packages\Mantis Shrimp\extra'
if msPath not in sys.path:
	sys.path.append(msPath)
rhDllPath = appDataPath + r'\Dynamo\0.9\packages\Mantis Shrimp\bin\Rhino3dmIO.dll'
clr.AddReferenceToFileAndPath(rhDllPath)

import Rhino as rc

#The inputs to this node will be stored as a list in the IN variable.
dataEnteringNode = IN
path = str(IN[0])

#Assign your output to the OUT variable
OUT = rc.FileIO.File3dm.Read(path)
