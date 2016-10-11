MantisShrimp
============

![Screenshot](http://archi-lab.net/wp-content/uploads/2014/10/Mantis_logo.png?width=600)


Mantis Shrimp is a Dynamo (Revit) and Grasshopper (Rhino) interoperability project that allows you to read Rhino's native *.3dm file type as well as export geometry from Grasshopper. It is written in Python in form of a user objects (on Grasshopper side for exporting) and custom Python nodes (on Dynamo side for importing). It's an OPEN SOURCE project with all of the source code available on this repository. At the moment it's a collaboration project between myself and Mostapha Sadeghipour, but feel free to join in. 

Couple things to check before you can get started:

  1. Exporting from Grasshopper uses a native IronPython2.7 module called pickle or cpickle. Make sure that your IronPython is installed in the default location C:\Program Files (x86)\IronPython 2.7. Again, unless you have specifically changed that location you should be good to go as its being installed by default when Dynamo is installed. 
  
  2. Make sure that you have GhPython plug-in for Grasshopper installed. All Mantis Shrimp User Objects for Grasshopper are written in Python so you will need that plug-in for them to work. Download it at: http://www.food4rhino.com/project/ghpython?ufh
  
  3. Interoperability with Grasshopper relies on RhinoCommon.dll which is the standard Rhino geometry library. Please make sure that when exporting geometry from Dynamo you are using the same version of RhinoCommon.dll as you are using to import it into Grasshopper and vice versa. Common mistake is to point Dynamo at a 64-bit based library while trying to import into a 32-bit based Rhino/Grasshopper and vice versa. To make sure that both versions align please use "SpecifyRhinoCommon.dll Path " node in Dynamo that can be found under MantisShrimp>Grasshopper>Setup
  
  4. Please make sure that you have latest updates installed for Rhino. There are some known conflicts that will happen if you are running just the base installation of Rhino without any updates (it fails to load certain plug-ins).
  
  5. Please make sure that you are using back-slashes or "\" in your file paths and not forward-slashes "/" as Windows operating system doesn't like that and will throw an eception.
  
  6. Please make sure that you have writing and reading rights for the specified file path. Lack of such rights will cause an error. 
  
  3. Watch these videos: http://archi-lab.net/?p=1486
  
License
============

Mantis Shrimp: A Plugin for Dynamo and Rhino/Grasshopper Interoperability (GPL) started by Konrad K Sobon

Copyright (c) 2014-pressent, Konrad K Sobon

Mantis Shrimp is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 3 of the License, or (at your option) any later version.

Mantis Shrimp is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with Mantis Shrimp; If not, see http://www.gnu.org/licenses/.

@license GPL-3.0+ http://spdx.org/licenses/GPL-3.0+
