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

pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

#The inputs to this node will be stored as a list in the IN variable.
dataEnteringNode = IN

if isinstance(IN[0], list):
	rhObjects = IN[0]
else:
	rhObjects = [IN[0]]

key = IN[1]

def GetValue(obj, key):
	try:
		if obj.Attributes.HasUserData:
			us = obj.Attributes.GetUserStrings()
			return us.Item[key]
	except:
		pass

def ProcessListArg(_func, _list, _arg):
    return map( lambda x: ProcessListArg(_func, x, _arg) if type(x)==list else _func(x, _arg), _list )

#extract user keys
try:
	errorReport = None
	rhValues = ProcessListArg(GetValue, rhObjects, key)
except:
	# if error accurs anywhere in the process catch it
	import traceback
	errorReport = traceback.format_exc()

#Assign your output to the OUT variable
if errorReport == None:
	OUT = rhValues
else:
	OUT = errorReport
