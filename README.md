MantisShrimp
============

![Screenshot](http://archi-lab.net/wp-content/uploads/2014/10/Mantis_logo.png?width=600)


Mantis Shrimp is a Dynamo (Revit) and Grasshopper (Rhino) interoperability project that allows you to read Rhino's native *.3dm file type as well as export geometry from Grasshopper. It is written in Python in form of a user objects (on Grasshopper side for exporting) and custom Python nodes (on Dynamo side for importing). It's an OPEN SOURCE project with all of the source code available on this repository. At the moment it's a collaboration project between myself and Mostapha Sadeghipour, but feel free to join in. 

Couple things to check before you can get started:

  1. Mantis Shrimp is written as custom Python nodes (Dynamo) so make sure that RhinoCommon.dll is the specified location. 
By default that location is where you would install Rhino C:\Program Files\Rhinoceros 5 (64-bit)\System so unless you have specifically changed that location while installing Rhino, you should be good to go. 

  2. Exporting from Grasshopper uses a native IronPython module called pickle or cpickle. Make sure that your IronPython is installed in the default location C:\Program Files (x86)\IronPython 2.7. Again, unless you have specifically changed that location you should be good to go. 

  3. Add Mantis Shrimp - Export component to your Grasshopper Special Folder>User Object or simply drag and drop onto Grasshopper canvas. Instructions can be found here: Link

  4. Add all of the Dynamo custom nodes to Dynamo's definitions folder or install them directly from Package Manager. Instructions can be found here: Link

  5. Read this Getting Started tutorial: Link

  6. Read this Export/Import example tutorial: Link
