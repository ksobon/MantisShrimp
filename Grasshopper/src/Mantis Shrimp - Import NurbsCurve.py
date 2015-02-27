#Copyright(c) 2015, Konrad K Sobon
#@arch_laboratory, http://archi-lab.net

"""
This component reads NurbsCurves exported from Dynamo

    Args:
        _filePath: path to file to read
        _import: boolean True or False that will either allow or prevent geometry \
            from being imported
"""
ghenv.Component.Name = "Mantis Shrimp - NurbsCurve"
ghenv.Component.NickName = 'DSNurbsCurve'
ghenv.Component.Category = "Mantis Shrimp"

import sys
import os
appDataPath = os.getenv('APPDATA')
msPath = appDataPath + r"\Dynamo\0.7\packages\Mantis Shrimp\extra"
if msPath not in sys.path:
    sys.path.append(msPath)
import mantisshrimp as ms
mantis = ms
reload(mantis)

from System import Array
from System.Collections.Generic import *
import cPickle as pickle
import Rhino as rc
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
import scriptcontext as sc

class SerializeObjects(object):
	def __init__(self, filePath, data = None):
		self.filePath = filePath
		self.data = data

	def saveToFile(self):
		with open(self.filePath, 'wb') as outf:
			pickle.dump(self.data, outf)

	def readFromFile(self):
		with open(self.filePath, 'rb') as inf:
			self.data = pickle.load(inf)

def process_list(_func, _list):
    return map( lambda x: process_list(_func, x) if type(x)==list else _func(x), _list )

def toRHObject(item):
    if type(item) == ms.MSNurbsCurve:
        return item.toRHNurbsCurve(sc.doc.ModelUnitSystem.ToString())

"""Transforms nestings of lists or tuples to a Grasshopper DataTree"""
"""Big thanks to Giulio Piacentino for this function"""
def list_to_tree(input, none_and_holes=False, source=[0]):
    def proc(input,tree,track):
        path = GH_Path(Array[int](track))
        if len(input) == 0 and none_and_holes: tree.EnsurePath(path); return
        for i,item in enumerate(input):
            if hasattr(item, '__iter__'): #if list or tuple
                track.append(i); proc(item,tree,track); track.pop()
            else:
                if none_and_holes: tree.Insert(item,path,i)
                elif item is not None: tree.Add(item,path)
    if input is not None: t=DataTree[object]();proc(input,t,source[:]);return t

if _import:
    serializer = SerializeObjects(_filePath)
    serializer.readFromFile()
    data = serializer.data
    dataList = process_list(toRHObject, data)
    outNurbsCurve = list_to_tree(dataList)
