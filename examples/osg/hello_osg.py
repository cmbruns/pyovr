
import os
from osgpypp import osgDB, osgViewer

this_dir = os.path.dirname(__file__)
cow_file = os.path.join(this_dir, 'cow.osg')
scene = osgDB.readNodeFile(cow_file)
viewer = osgViewer.Viewer()
viewer.setSceneData(scene)
viewer.setUpViewInWindow(100, 100, 500, 500, 0)
viewer.run()
