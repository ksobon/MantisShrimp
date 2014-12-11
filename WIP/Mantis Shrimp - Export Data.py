#Copyright(c) 2014, Konrad K Sobon
#@arch_laboratory, http://archi-lab.net

"""
This component exports serialized geometry to specified location.
Thank you to Mostapha Sadeghipour Roudsari for providing invaluable
help with this project. 

    Args:
        _data: data like strings, integers etc
        _filePath: A local folder with file name and extension ex. C:\test.geo
        _export: Set Boolean to True to export data to destination folder
"""

ghenv.Component.Name = "Mantis Shrimp - DataExport"
ghenv.Component.NickName = 'exportData'
ghenv.Component.Category = "Mantis Shrimp"

import sys
# change this to where you library is
sys.path.append(r"C:\Users\ksobon\AppData\Roaming\Dynamo\0.7\packages\Mantis Shrimp\extra")
from mantisshrimp import *

import Rhino as rc
import cPickle as pickle
import os
import Grasshopper.Kernel as gh

class SerializeObjects(object):
    
    def __init__(self, filePath, data = None):
        
        # create directory if it is not created
        folder, fileName = os.path.split(filePath)
        if not os.path.isdir(folder):
            os.mkdir(folder)
        
        self.filePath = filePath
        self.data = data
   
    def convertPolyCurveToCurve(self):
        placeHolder = range(len(self.data))
        
        for geoCount, geo in enumerate(self.data):
            if type(geo) == rc.Geometry.PolyCurve:
                placeHolder[geoCount] = geo.ToNurbsCurve()
            else:
                placeHolder[geoCount] = geo
        
        self.data = placeHolder
        
    def saveToFile(self):
        try:
            with open(self.filePath, 'wb') as outf:
                pickle.dump(self.data, outf)
        except:
            # check input data and convert PolyCurves to NurbsCurve
            # In some cases pickle crashes while exporting polycurves
            self.convertPolyCurveToCurve()
            with open(self.filePath, 'wb') as outf:
                pickle.dump(self.data, outf)
            
    def readFromFile(self):
        with open(self.filePath, 'rb') as inf:
            self.data = pickle.load(inf)

# written by Giulio Piacentino, giulio@mcneel.com
def TreeToList(input, RetrieveBase = lambda x: x[0]):
    """Returns a list representation of a Grasshopper DataTree"""
    def extend_at(path, index, simple_input, rest_list):
        target = path[index]
        if len(rest_list) <= target: rest_list.extend([None]*(target-len(rest_list)+1))
        if index == path.Length - 1:
            rest_list[target] = list(simple_input)
        else:
            if rest_list[target] is None: rest_list[target] = []
            extend_at(path, index+1, simple_input, rest_list[target])
    all = []
    for i in range(input.BranchCount):
        path = input.Path(i)
        extend_at(path, 0, input.Branch(path), all)
    return RetrieveBase(all)

# convert incoming DataTree to Python List object
dataOut = MSData(TreeToList(_data))

if _export:
    try:
        serializer = SerializeObjects(filePath, dataOut)
        serializer.saveToFile()
        warnType = gh.GH_RuntimeMessageLevel.Remark
        msg = "File is exported to " + filePath + "Now you can use Dynamo to import the file."
    except Exception, e:
        warnType = gh.GH_RuntimeMessageLevel.Warning
        msg = "Failed to export: \n" + `e`
else:
    msg = "Export set to false."

ghenv.Component.AddRuntimeMessage(warnType, msg)
