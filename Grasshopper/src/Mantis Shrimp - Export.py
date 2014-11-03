#Copyright(c) 2014, Konrad K Sobon
#@arch_laboratory, http://archi-lab.net

"""
This component exports serialized geometry to specified location. Thank you to Mostapha Sadeghipour Roudsari
for providing invaluable help with this project. 

    Args:
        _geometry: any GH/or rhino referenced geometry
        _filePath: A local folder with file name and extension ex. C:\test.geo
        _export: Set Boolean to True to export geometry to destination folder
"""

ghenv.Component.Name = "Mantis Shrimp - Export"
ghenv.Component.NickName = 'exportMantisShrimp'
ghenv.Component.Category = "Mantis Shrimp"

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



if _export:
    try:
        serializer = SerializeObjects(_filePath, _geometry)
        serializer.saveToFile()
        
        warnType = gh.GH_RuntimeMessageLevel.Remark
        msg = "File is exported to " + _filePath + ".\n" + \
              "Now you can use Dynamo to import the file."
    except Exception, e:
        warnType = gh.GH_RuntimeMessageLevel.Warning
        msg = "Failed to export: \n" + `e`
    
    ghenv.Component.AddRuntimeMessage(warnType, msg)
        