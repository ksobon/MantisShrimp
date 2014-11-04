#Copyright(c) 2014, Konrad K Sobon
#@arch_laboratory, http://archi-lab.net

"""
This component attaches string data to geometry via UserStrings. 

    Args:
        _geometry: any GH/or rhino referenced geometry
        _keys: a list of user defined keys
        _values: a list of user defined values (will be converted to strings)
"""

for i,j in zip(_keys, _values):
    _geometry.SetUserString(str(i), str(j))
outGeometry = _geometry
