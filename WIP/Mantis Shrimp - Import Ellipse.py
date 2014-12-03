#Copyright(c) 2014, Konrad K Sobon
#@arch_laboratory, http://archi-lab.net

"""
This component reads ellipses exported from Dynamo

    Args:
        _filePath: path to file to read
        _import: boolean True or False that will either allow or prevent geometry \
            from being imported
"""
ghenv.Component.Name = "Mantis Shrimp - Ellipse"
ghenv.Component.NickName = 'DSEllipse'
ghenv.Component.Category = "Mantis Shrimp"

import sys
ms_path = r'C:\\Users\\ksobon\\AppData\\Roaming\\Dynamo\\0.7\\packages\\Mantis Shrimp\\extra'
if ms_path not in sys.path:
    sys.path.append(ms_path)
import mantisshrimp as ms
mantis = mantisshrimp
reload(mantis)

import Rhino as rc
import cPickle as pickle
import os
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
from System import Array
from System.Collections.Generic import *

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

serializer = SerializeObjects(_filePath)
serializer.readFromFile()
data = serializer.data

# recursive function to process any input list and output 
# matching structure list
def process_list(_func, _list):
    return map( lambda x: process_list(_func, x) if type(x)==list else _func(x), _list )

def toRHObject(item):
    if type(item) == ms.MSEllipse:
        return item.toRHEllipse()

if _import:
    _tree = DataTree[rc.Geometry.Ellipse]()
    some_data = process_list(toRHObject, data)
    someList = Array[Array[rc.Geometry.Ellipse]](map(tuple, some_data))
#    outEllipses = _tree.AddRange(someList)

print(someList)
