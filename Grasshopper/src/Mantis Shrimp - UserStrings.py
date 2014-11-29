#Copyright(c) 2014, Konrad K Sobon
#@arch_laboratory, http://archi-lab.net

"""
This component attaches string data to geometry via UserStrings. 

    Args:
        _geometry: any GH/or rhino referenced geometry
        _keys: a list of user defined keys
        _values: a list of user defined values (will be converted to strings)
"""

outGeometry = []
for index, geo in enumerate(_geometry):
    for i, j in zip(list(_keys.Branches[index]), list(_values.Branches[index])):
        geo.SetUserString(str(i), str(j))
    outGeometry.append(geo)
