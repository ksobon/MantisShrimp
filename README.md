MantisShrimp
============

![Screenshot](http://archi-lab.net/wp-content/uploads/2014/10/Mantis_logo.png?width=600)


Mantis Shrimp is a Dynamo (Revit) and Grasshopper (Rhino) interoperability project that allows you to read Rhino's native *.3dm file type as well as export geometry from Grasshopper. It is written in Python in form of a user objects (on Grasshopper side for exporting) and custom Python nodes (on Dynamo side for importing). It's an OPEN SOURCE project with all of the source code available on this repository. At the moment it's a collaboration project between myself and Mostapha Sadeghipour, but feel free to join in. 

Couple things to check before you can get started:

  1. Mantis Shrimp is written as custom Python nodes (Dynamo) so make sure that RhinoCommon.dll is in the specified location. 
By default that location is where you would install Rhino C:\Program Files\Rhinoceros 5 (64-bit)\System so unless you have specifically changed that location while installing Rhino, you should be good to go. 
It was brought to my attention that in some cases that default location is actually C:\Program Files\Rhinoceros 5.0 (64-bit)\System or even C:\Program Files\Rhinoceros 5.0\System. I have added these paths to default search that every node will perform. 

  2. Exporting from Grasshopper uses a native IronPython2.7 module called pickle or cpickle. Make sure that your IronPython is installed in the default location C:\Program Files (x86)\IronPython 2.7. Again, unless you have specifically changed that location you should be good to go as its being installed by default when Dynamo is installed. 
  
  3. Make sure that you have GhPython plug-in for Grasshopper installed. All Mantis Shrimp User Objects for Grasshopper are written in Python so you will need that plug-in for them to work. Download it at: http://www.food4rhino.com/project/ghpython?ufh 

  4. Add Mantis Shrimp - Export component to your Grasshopper Special Folder>User Object or simply drag and drop onto Grasshopper canvas. Instructions can be found here: http://archi-lab.net/?p=540

  5. Add all of the Dynamo custom nodes to Dynamo's definitions folder or install them directly from Package Manager. Instructions can be found here: http://archi-lab.net/?p=540

  6. Read this Getting Started tutorial: http://archi-lab.net/?p=540

  7. Read this Export/Import example tutorial: http://archi-lab.net/?p=554

  8. Read this Export/Import 3dm files, example tutorial: http://archi-lab.net/?p=578
