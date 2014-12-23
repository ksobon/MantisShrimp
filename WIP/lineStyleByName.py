#Copyright(c) 2014, Konrad Sobon
# @arch_laboratory, http://archi-lab.net

import clr
clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *

# Import DocumentManager and TransactionManager
clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

# Import RevitAPI
clr.AddReference("RevitAPI")
import Autodesk
from Autodesk.Revit.DB import *

doc = DocumentManager.Instance.CurrentDBDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application

from System.Collections.Generic import *

#The inputs to this node will be stored as a list in the IN variable.
dataEnteringNode = IN

name = IN[0]

#gStyles = FilteredElementCollector(doc).OfClass(GraphicsStyle).ToElements()
#lineStyle = None
#for i in gStyles:
#	if i.Name == styleName and i.GraphicsStyleCategory.Parent.Name == "Lines":
#		lineStyle = i
#		break

lineStyles = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Lines)
replacementStyles = []
try:
	replacementStyles.append(next(i.LineStyle for i in lineStyles if name==i.LineStyle.Name))
except StopIteration:
	pass

OUT = replacementStyles
