# Copyright(c) 2015, Konrad Sobon
# @arch_laboratory, http://archi-lab.net

import clr
import sys

pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

import os
appDataPath = os.getenv('APPDATA')
dynVersions = ["0.7", "0.8", "0.9"]
dynFolders = ["extra", "bin"]
for i in dynVersions:
	for j in dynFolders:
		part1 = "\\Dynamo\\"
		version = i
		part2 = "\\packages\\Mantis Shrimp\\"
		folder = j
		msPath = appDataPath + part1 + version + part2 + folder
		if j == "extra":
			if msPath not in sys.path:
				sys.path.Add(msPath)
		if j == "bin":
			dllName = "\\Rhino3dmIO.dll"
			rhDllPath = appDataPath + part1 + version + part2 + folder + dllName
			if msPath not in sys.path:
				sys.path.Add(msPath)
				if os.path.isfile(rhDllPath):
					clr.AddReferenceToFileAndPath(rhDllPath)

import Rhino as rc

#The inputs to this node will be stored as a list in the IN variable.
dataEnteringNode = IN
rhModel = IN[0]

#extract layer names from 3dm file
rhLayers = []
for i in rhModel.Layers:
	rhLayers.append(i.Name)

#Assign your output to the OUT variable
OUT = rhLayers
